from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .constants import SubscriptionLimitMap, SubscriptionStatusChoices
from .models import Subscription



@receiver(post_save, sender=Subscription)
def provision_subscription(sender, instance, created, **kwargs):
    agency = instance.customer.agency
    # if instance.status == SubscriptionStatusChoices.ACTIVE:
    #     if SubscriptionLimitMap[instance.stripe_id]['type'] == 'plan':
    #         agency.amount_of_biodata_allowed = SubscriptionLimitMap[
    #             instance.stripe_id
    #         ]['biodata']
    #         agency.amount_of_documents_allowed = SubscriptionLimitMap[
    #             instance.stripe_id
    #         ]['documents']
    #         agency.amount_of_employees_allowed = SubscriptionLimitMap[
    #             instance.stripe_id
    #         ]['employee_accounts']
    #     elif (
    #         SubscriptionLimitMap[
    #             instance.stripe_id
    #         ]['name'] == 'Featured Maid Advertisement'
    #     ):
    #         # amt_feat_bio_allowed = Subscription.objects.filter(
    #         #     agency=agency,
    #         #     product=product,
    #         #     end_date_gt=timezone.now()
    #         # ).count()
    #         agency.amount_of_featured_biodata_allowed = amt_feat_bio_allowed

    # elif instance.status == SubscriptionStatusChoices.CANCELED:
    #     agency.active = False

    # agency.save()
