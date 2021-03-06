from django.db import models
from django.utils.translation import ugettext_lazy as _

class SubscriptionStatusChoices(models.TextChoices):
    INCOMPLETE = 'INCOMPLETE', _('Incomplete')
    INCOMPLETE_EXPIRED = 'INCOMPLETE_EXPIRED', _('Incomplete (Expired)')
    TRIALING = 'TRIALING', _('Trialing')
    ACTIVE = 'ACTIVE', _('Active')
    PAST_DUE = 'PAST_DUE', _('Past Due')
    CANCELED = 'CANCELED', _('Canceled')
    UNPAID = 'UNPAID', _('Unpaid')
    
SubscriptionLimitMap = {
    "prod_IlJqpv40JRgCa6": {
        "name": "Premium Platform & CRM Plan",
        "biodata": 200,
        "documents": 200,
        "employee_accounts": 12
    },
    "prod_IlJiwIHP2LXuRI": {
        "name": "Standard Platform & CRM Plan",
        "biodata": 100,
        "documents": 100,
        "employee_accounts": 8
    },
    "prod_IlJnULpKUetaRc": {
        "name": "Premium CRM Plan",
        "biodata": 0,
        "documents": 200,
        "employee_accounts": 12
    },
    "prod_IlJf58jk8siXvV": {
        "name": "Standard CRM Plan",
        "biodata": 0,
        "documents": 100,
        "employee_accounts": 8
    },
    "prod_IlJl5XiqUt2O3Q": {
        "name": "Premium Platform Plan",
        "biodata": 200,
        "documents": 0,
        "employee_accounts": 12
    },
    "prod_IlJVbv4ixfNtNg": {
        "name": "Standard Platform Plan",
        "biodata": 100,
        "documents": 0,
        "employee_accounts": 8
    }
}