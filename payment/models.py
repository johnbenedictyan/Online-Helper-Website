# Imports from python

# Imports from django
from django.db import models

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

