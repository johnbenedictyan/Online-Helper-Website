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
    
SubscriptionBiodataLimitChoicesMap = {
    "prod_IlJqpv40JRgCa6": 200,
    "prod_IlJl5XiqUt2O3Q": 200,
    "prod_IlJiwIHP2LXuRI": 100,
    "prod_IlJVbv4ixfNtNg": 100,
}