import stripe
from advertisement.models import Advertisement
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from maid.models import Maid
from payment.models import Customer

from .models import Agency, AgencyEmployee, PotentialAgency

# Start of Signals


@receiver(post_save, sender=Agency)
def agency_created(sender, instance, created, **kwargs):
    if created:
        try:
            pa = PotentialAgency.objects.get(
                license_number=instance.license_number
            )
        except PotentialAgency.DoesNotExist as e:
            print(e)
        else:
            pa.delete()


@receiver(post_save, sender=Agency)
def stripe_customer_created_or_update(sender, instance, created, **kwargs):
    agency = instance
    if created:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            stripe_customer = stripe.Customer.create(
                address={
                    'city': 'Singapore',
                    'country': 'Singapore',
                    'line1': agency.get_main_branch().address_1,
                    'line2': agency.get_main_branch().address_2,
                    'postal_code': agency.get_main_branch().postal_code,
                    'state': 'Singapore',
                },
                description=f'Customer account for {agency.name}',
                email=None,
                name=agency.name,
                invoice_settings={
                    'custom_fields': None,
                    'default_payment_method': None,
                    'footer': ''
                }
            )
        except Exception as e:
            print(e)
        else:
            new_customer = Customer(
                agency=agency
            )
            new_customer.id = stripe_customer.id
            new_customer.save()
    else:
        pass


@receiver(post_save, sender=AgencyEmployee)
def agency_employee_counter(sender, instance, created, **kwargs):
    agency = instance.agency
    agency.amount_of_employees = AgencyEmployee.objects.filter(
        agency=agency
    ).count()
    agency.save()


@receiver(post_save, sender=Agency)
def deactivate_agency(sender, instance, created, **kwargs):
    agency = instance
    if not agency.active:
        Maid.objects.filter(
            agency=agency
        ).update(
            frozen=True
        )
        Advertisement.objects.filter(
            agency=agency
        ).update(
            frozen=True
        )


@receiver(pre_save, sender=Agency)
def reactivate_agency(sender, instance, **kwargs):
    if instance.id:
        current = instance
        prev = agency = Agency.objects.get(
            pk=instance.pk
        )
        if not prev.active and current.active:
            Maid.objects.filter(
                agency=agency
            ).update(
                frozen=False
            )
            Advertisement.objects.filter(
                agency=agency
            ).update(
                frozen=False
            )
