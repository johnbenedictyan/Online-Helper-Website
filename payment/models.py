from agency.models import Agency
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .constants import PlanIntervals, PlanType, planStatusChoices


class Invoice(models.Model):
    agency = models.ForeignKey(
        Agency,
        on_delete=models.SET_NULL,
        related_name='invoices',
        null=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )


class Customer(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=255
    )

    agency = models.OneToOneField(
        Agency,
        on_delete=models.CASCADE,
        related_name='customer_account'
    )


class Subscription(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    price = models.PositiveIntegerField(
        verbose_name=_('Price in cents')
    )

    start_date = models.DateTimeField(
        editable=False,
        null=True
    )

    end_date = models.DateTimeField(
        editable=False,
        null=True
    )

    status = models.CharField(
        verbose_name=_('Subscription\'s status'),
        max_length=18,
        choices=planStatusChoices.choices,
        default=planStatusChoices.INCOMPLETE
    )

    interval = models.CharField(
        verbose_name=_('Subscription interval'),
        max_length=7,
        choices=PlanIntervals.choices,
        default=PlanIntervals.THREE_MONTH
    )

    subscription_type = models.CharField(
        verbose_name=_('Subscription type'),
        max_length=13,
        choices=PlanType.choices,
        default=PlanType.BASIC_PLAN
    )

    stripe_id = models.CharField(
        verbose_name=_('Stripe ID'),
        max_length=255
    )
