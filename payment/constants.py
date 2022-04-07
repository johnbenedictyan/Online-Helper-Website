from django.db import models
from django.utils.translation import ugettext_lazy as _


class planStatusChoices(models.TextChoices):
    INCOMPLETE = 'INCOMPLETE', _('Incomplete')
    INCOMPLETE_EXPIRED = 'INCOMPLETE_EXPIRED', _('Incomplete (Expired)')
    TRIALING = 'TRIALING', _('Trialing')
    ACTIVE = 'ACTIVE', _('Active')
    PAST_DUE = 'PAST_DUE', _('Past Due')
    CANCELED = 'CANCELED', _('Canceled')
    UNPAID = 'UNPAID', _('Unpaid')


class planTypeChoices(models.TextChoices):
    PLAN = 'PLAN', _('Plan')
    ADVERTISEMENT = 'AD', _('Advertisement')


class PlanIntervals(models.TextChoices):
    ONE_MONTH = '1month', _('1 Month')
    THREE_MONTH = '3month', _('3 Month')
    SIX_MONTH = '6month', _('6 Month')
    TWELVE_MONTH = '12month', _('12 Month')


class PlanType(models.TextChoices):
    BASIC_PLAN = 'Basic Plan', _('Basic Plan')
    STANDARD_PLAN = 'Standard Plan', _('Standard Plan')
    PREMIUM_PLAN = 'Premium Plan', _('Premium Plan')
    ADVERTISEMENT = 'Advertisement', _('Advertisement')


planLimitMap = {
    'price_1JiDNRKvEbGNaxrCspFPthnv': {
        'product_id': 'prod_KMxIAjOOMeB715',
        'name': 'Enquiry Page Advertisement',
        'type': 'advertisement'
    },
    'price_1JiDNEKvEbGNaxrCwtEfXyvE': {
        'product_id': 'prod_KMxHCih6IAWrdo',
        'name': 'About Us Page Advertisement',
        'type': 'advertisement'
    },
    'price_1JiDN3KvEbGNaxrCAy8gIQnx': {
        'product_id': 'prod_KMxHADq5DgOpG3',
        'name': 'Maid Agencies Page Advertisement',
        'type': 'advertisement'
    },
    'price_1JiDMrKvEbGNaxrCGCynlMZq': {
        'product_id': 'prod_KMxHxjGvHaPcKB',
        'name': 'FAQ Page Advertisement',
        'type': 'advertisement'
    },
    'price_1JiDLhKvEbGNaxrCbve8hrAs': {
        'product_id': 'prod_KMxGC7oZoeDiEx',
        'name': 'Maid Profile Page Advertisement',
        'type': 'advertisement'
    },
    'price_1JiDLTKvEbGNaxrC5GFhgCp4': {
        'product_id': 'prod_KMxFdtF6AXrwKG',
        'name': 'Search Maid Page Advertisement',
        'type': 'advertisement'
    },
    'price_1JiDKqKvEbGNaxrCmRmD6Vsm': {
        'product_id': 'prod_KMxFrMhwC6fQTz',
        'name': 'Home Page Advertisement',
        'type': 'advertisement'
    },
    'price_1JMn4wKvEbGNaxrCvpY4fVig': {
        'product_id': 'prod_J438kMRsmpiPZR',
        'name': 'Featured Maid Advertisement',
        'type': 'advertisement'
    },
    'price_1JiDG3KvEbGNaxrCzejJlKlD': {
        'product_id': 'prod_IlJqpv40JRgCa6',
        'name': 'Premium Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JiDFvKvEbGNaxrCOwAIX2AY': {
        'product_id': 'prod_IlJqpv40JRgCa6',
        'name': 'Premium Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JiDFmKvEbGNaxrCaSPhrjuF': {
        'product_id': 'prod_IlJqpv40JRgCa6',
        'name': 'Premium Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JiDEsKvEbGNaxrCVpVu3tC9': {
        'product_id': 'prod_IlJiwIHP2LXuRI',
        'name': 'Standard Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JiDEiKvEbGNaxrCPMeCw5VT': {
        'product_id': 'prod_IlJiwIHP2LXuRI',
        'name': 'Standard Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JiDEaKvEbGNaxrC42CnkoLe': {
        'product_id': 'prod_IlJiwIHP2LXuRI',
        'name': 'Standard Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JMn8FKvEbGNaxrCvTyY5Ym6': {
        'product_id': 'prod_K0olZqTcT0jErR',
        'name': 'Basic Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JMn8FKvEbGNaxrChQji3o1u': {
        'product_id': 'prod_K0olZqTcT0jErR',
        'name': 'Basic Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    },
    'price_1JMn8FKvEbGNaxrCyjESuW6Y': {
        'product_id': 'prod_K0olZqTcT0jErR',
        'name': 'Basic Platform & CRM Plan',
        'type': 'plan',
        'biodata': 200,
        'documents': 200,
        'employee_accounts': 10
    }
}
# "prod_IlJqpv40JRgCa6": {
#     "name": "Premium Platform & CRM Plan",
#     "type": "plan",
#     "biodata": 200,
#     "documents": 200,
#     "employee_accounts": 12
# },
# "prod_IlJiwIHP2LXuRI": {
#     "name": "Standard Platform & CRM Plan",
#     "type": "plan",
#     "biodata": 100,
#     "documents": 100,
#     "employee_accounts": 8
# },
# "prod_IlJnULpKUetaRc": {
#     "name": "Premium CRM Plan",
#     "type": "plan",
#     "biodata": 0,
#     "documents": 200,
#     "employee_accounts": 12
# },
# "prod_IlJf58jk8siXvV": {
#     "name": "Standard CRM Plan",
#     "type": "plan",
#     "biodata": 0,
#     "documents": 100,
#     "employee_accounts": 8
# },
# "prod_IlJl5XiqUt2O3Q": {
#     "name": "Premium Platform Plan",
#     "type": "plan",
#     "biodata": 200,
#     "documents": 0,
#     "employee_accounts": 12
# },
# "prod_IlJVbv4ixfNtNg": {
#     "name": "Standard Platform Plan",
#     "type": "plan",
#     "biodata": 100,
#     "documents": 0,
#     "employee_accounts": 8
# },
# "prod_J434xmRtR0HI8c": {
#     "name": "Premium Advertisement",
#     "type": "advertisement"
# },
# "prod_J436TNwqM3fOBW": {
#     "name": "Standard Advertisement",
#     "type": "advertisement",
# },
# "prod_J438kMRsmpiPZR": {
#     "name": "Featured Maid Advertisement",
#     "type": "advertisement",
# }
# }
