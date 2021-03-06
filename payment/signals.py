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
    if instance.status == SubscriptionStatusChoices.ACTIVE:
        agency = instance.customer.agency
        product = instance.product
        agency.amount_of_biodata  = SubscriptionBiodataLimitChoicesMap[
            product.pk
        ]
        agency.save()