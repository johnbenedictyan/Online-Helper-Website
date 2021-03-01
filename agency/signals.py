# Imports from python

# Imports from django
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Imports from other apps
import stripe
from payment.models import Customer

# Imports from within the app
from .models import Agency, AgencyBranch, AgencyOperatingHours, PotentialAgency

# Utiliy Classes and Functions
def agency_completed(agency):
    """ This function will check if the branch_complete and
        operating_hours_complete booleans are True.
        If they are both true then the function will set the agency complete
        field to True.

    Args:
        agency ([obj]): [The agency model object]
    """
    if(
        agency.branch_complete == True and 
        agency.operating_hours_complete == True
    ):
        agency.completed = True
        agency.save()


# Start of Signals
@receiver(post_save, sender=Agency)
def agency_created(sender, instance, created, **kwargs):
    if created == True:
        try:
            pa = PotentialAgency.objects.get(
                license_number = instance.license_number
            )
        except PotentialAgency.DoesNotExist as e:
            print(e)
        else:
            pa.delete()

@receiver(post_save, sender=AgencyBranch)
def agency_location_completed(sender, instance, created, **kwargs):
    if created == False:
        agency = instance.agency
        branch_values = list(instance.__dict__.values())
        if '' in branch_values:
            branch_valid = False
        else:
            branch_valid = True
        
        if branch_valid == True:
            agency.branch_complete = branch_valid
        
            if(
                agency.branch_complete == True and 
                agency.operating_hours_complete == True
            ):
                agency.completed = True
                agency.save()
            else:
                agency.save()

@receiver(post_save, sender=AgencyOperatingHours)
def agency_operating_hours_completed(sender, instance, created, **kwargs):
    if created == False:
        agency = instance.agency
        operating_hours_values = list(instance.__dict__.values())
        
        if '' in operating_hours_values:
            operating_hours_valid = False
        else:
            operating_hours_valid = True
        
        if operating_hours_valid == True:
            agency.operating_hours_complete = operating_hours_valid
        
            if(
                agency.branch_complete == True and 
                agency.operating_hours_complete == True
            ):
                agency.completed = True
                agency.save()
            else:
                agency.save()

@receiver(post_save, sender=Agency)
def stripe_customer_created_or_update(sender, instance, created, **kwargs):
    agency = instance
    if created == True:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            stripe_customer = stripe.Customer.create(
                address = {
                    'city': None,
                    'country': None,
                    'line1': None,
                    'line2': None,
                    'postal_code': None,
                    'state': None,
                },
                description = f'Customer account for {agency.name}',
                email=agency.company_email,
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
                agency = agency
            )
            new_customer.id = stripe_customer.id
            new_customer.save()
    else:
        pass