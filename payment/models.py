# Imports from python

# Imports from django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Imports from project

# Imports from other apps
from agency.models import Agency

# Imports from within the app

# Utiliy Classes and Functions

# Start of Models

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
    agency = models.OneToOneField(
        Agency,
        on_delete=models.CASCADE,
        related_name='customer_account'
    )
    stripe_customer_id = models.CharField(
        verbose_name=_('Stripe\'s customer id'),
        max_length=255
    )