from agency.models import Agency
from django.db import models
from django.utils.translation import ugettext_lazy as _
from onlinemaid.storage_backends import PublicMediaStorage


class AdvertisementLocation(models.Model):
    class AdvertisementTierChoices(models.TextChoices):
        STANDARD = 'STANDARD', _('Standard')
        PREMIUM = 'PREMIUM', _('Premium')

    name = models.CharField(
        verbose_name=_('Page name'),
        max_length=30
    )

    tier = models.CharField(
        verbose_name=_('Advertisment tier'),
        max_length=8,
        choices=AdvertisementTierChoices.choices,
        default=AdvertisementTierChoices.STANDARD
    )

    total_amount_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Total number of allowed advertisements'),
        default=5
    )


class Advertisement(models.Model):
    class AdvertisementTypeChoices(models.TextChoices):
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
        choices=AdvertisementTypeChoices.choices,
        default=AdvertisementTypeChoices.BANNER
    )

    start_date = models.DateTimeField(
        verbose_name=_('Advertisment start date'),
        null=True,
        editable=False
    )

    end_date = models.DateTimeField(
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

    photo = models.FileField(
        verbose_name=_('Advertisement Photo'),
        null=True,
        storage=PublicMediaStorage()
    )

    remarks = models.TextField(
        verbose_name=_('Testimonial statment'),
        null=True
    )

    frozen = models.BooleanField(
        default=False,
        editable=False
    )
