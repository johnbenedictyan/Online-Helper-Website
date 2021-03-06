# Imports from python

# Imports from django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Imports from other apps

# Imports from within the app
from .constants import (
    SubscriptionStatusChoices, SubscriptionBiodataLimitChoicesMap
)

from .models import (
    Customer, SubscriptionProduct, SubscriptionProductImage, 
    SubscriptionProductPrice, Subscription
)



# Start of Signals
@receiver(post_save, sender=Subscription)
def provision_subscription(sender, instance, created, **kwargs):
    agency = instance.customer.agency
    product = instance.product
    if instance.status == SubscriptionStatusChoices.ACTIVE:
        agency.amount_of_biodata_allowed  = SubscriptionBiodataLimitChoicesMap[
            product.pk
        ]
    elif instance.status == SubscriptionStatusChoices.CANCELED:
        agency.active = False
        
    agency.save()