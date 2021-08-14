# Global Imports

# Django Imports
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Project Apps Imports

# App Imports
from .constants import (
    SubscriptionStatusChoices, SubscriptionLimitMap
)

from .models import Subscription


# Start of Signals
@receiver(post_save, sender=Subscription)
def provision_subscription(sender, instance, created, **kwargs):
    agency = instance.customer.agency
    product = instance.product
    if instance.status == SubscriptionStatusChoices.ACTIVE:
        if SubscriptionLimitMap[product.pk]['type'] == 'plan':
            agency.amount_of_biodata_allowed = SubscriptionLimitMap[
                product.pk
            ]['biodata']
            agency.amount_of_documents_allowed = SubscriptionLimitMap[
                product.pk
            ]['documents']
            agency.amount_of_employees_allowed = SubscriptionLimitMap[
                product.pk
            ]['employee_accounts']
        elif (
                SubscriptionLimitMap[
                    product.pk
                ]['name'] == 'Featured Maid Advertisement'
            ):
            agency.amount_of_featured_biodata_allowed = Subscription.objects.filter(
                agency=agency,
                product=product,
                end_date_gt=timezone.now()
            ).count()

    elif instance.status == SubscriptionStatusChoices.CANCELED:
        agency.active = False

    agency.save()
