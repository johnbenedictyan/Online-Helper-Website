# Imports from python

# Imports from django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Imports from other apps
from agency.models import Agency

# Imports from within the app

# Utiliy Classes and Functions

# Start of Models

class AdvertisementLocation(models.Model):
    class AdvertisementTierChoices(models.TextChoices):
        NONE = 'NONE', _('None')
        TIER_1 = 'TIER1', _('Tier 1')
        TIER_2 = 'TIER2', _('Tier 2')
        TIER_3 = 'TIER3', _('Tier 3')

    name = models.CharField(
        verbose_name=_('Page name'),
        max_length=30,
        blank=False
    )

    tier = models.CharField(
        verbose_name=_('Advertisment tier'),
        max_length=5,
        blank=False,
        choices=AdvertisementTierChoices.choices,
        default=AdvertisementTierChoices.NONE
    )

class Advertisement(models.Model):
    class AdvertisementTypeChoices(models.TextChoices):
        NONE = 'NONE', _('None')
        BANNER = 'BANNER', _('Banner')
        TESTIMONIAL = 'TESTI', _('Testimonial')

    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='advertisements'
    )

    location = models.ForeignKey(
        AdvertisementLocation,
        on_delete=models.CASCADE,
        related_name='advertisements'
    )

    ad_type = models.CharField(
        verbose_name=_('Advertisment type'),
        max_length=6,
        blank=False,
        choices=AdvertisementTypeChoices.choices,
        default=AdvertisementTypeChoices.NONE
    )

    start_date = models.DateTimeField(
        verbose_name=_('Advertisment start date'),
        null=True,
        editable=False
    )

    start_date = models.DateTimeField(
        verbose_name=_('Advertisment end date'),
        null=True,
        editable=False
    )

    approved = models.BooleanField(
        verbose_name=_('Approved'),
        default=False,
        editable=False
    )

    paid = models.BooleanField(
        verbose_name=_('Paid'),
        default=False,
        editable=False
    )
