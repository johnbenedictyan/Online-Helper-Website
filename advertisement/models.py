import math
from datetime import date, datetime, timedelta

from agency.models import Agency
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
# from onlinemaid.storage_backends import PublicMediaStorage


class QuarterChoices(models.TextChoices):
    ONE = '1', _('First Quarter')
    TWO = '2', _('Second Quarter')
    THREE = '3', _('Third Quarter')
    FOUR = '4', _('Fourth Quarter')


class YearChoices(models.TextChoices):
    TWENTY_TWENTY_ONE = '2021', _('2021')
    TWENTY_TWENTY_TWO = '2022', _('2022')
    TWENTY_TWENTY_THREE = '2023', _('2023')
    TWENTY_TWENTY_FOUR = '2024', _('2024')
    TWENTY_TWENTY_FIVE = '2025', _('2025')


class AdvertisementLocation(models.Model):
    name = models.CharField(
        verbose_name=_('Page name'),
        max_length=30
    )

    stripe_price_id = models.CharField(
        verbose_name=_('Advertisement Stripe ID'),
        max_length=255,
        null=True
    )

    total_amount_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Total number of allowed advertisements per quarter'),
        default=5
    )

    price = models.PositiveSmallIntegerField(
        verbose_name=_('Price'),
        default=0
    )

    active = models.BooleanField(
        default=True
    )

    def get_current_quarter(self):
        return (datetime.now().month - 1) // 3 + 1

    def get_current_year(self):
        return datetime.now().year

    def get_slots(self):
        if self.get_current_year() == 2021:
            year_choice = YearChoices.TWENTY_TWENTY_ONE
        elif self.get_current_year() == 2022:
            year_choice = YearChoices.TWENTY_TWENTY_TWO
        elif self.get_current_year() == 2023:
            year_choice = YearChoices.TWENTY_TWENTY_THREE
        elif self.get_current_year() == 2024:
            year_choice = YearChoices.TWENTY_TWENTY_FOUR

        if self.get_current_quarter == 1:
            return [
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.ONE,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ],
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.TWO,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ],
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.THREE,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ],
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.FOUR,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ]
            ]
        elif self.get_current_quarter == 2:
            return [
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.TWO,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ],
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.THREE,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ],
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.FOUR,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ]
            ]
        elif self.get_current_quarter == 3:
            return [
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.THREE,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ],
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.FOUR,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ]
            ]
        else:
            return [
                [
                    self.total_amount_allowed - self.advertisements.filter(
                        quarter=QuarterChoices.FOUR,
                        year=year_choice
                    ).count(),
                    self.total_amount_allowed,
                    self.advertisements.count() >= self.total_amount_allowed
                ]
            ]

    def get_name(self):
        return (self.name.replace("_ad", " Page Advertisement")).title()

    def set_purge(self):
        purgeable_ad_requests = [
            x for x in self.advertisements if x.is_purgeable()
        ]
        for ad in purgeable_ad_requests:
            ad.delete()


class Advertisement(models.Model):
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

    quarter = models.CharField(
        max_length=1,
        choices=QuarterChoices.choices,
        default=QuarterChoices.ONE
    )

    year = models.CharField(
        max_length=4,
        choices=YearChoices.choices,
        default=YearChoices.TWENTY_TWENTY_ONE
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

    time_created = models.DateTimeField(
        default=timezone.now
    )

    def get_current_quarter(self):
        return (datetime.now().month - 1) // 3 + 1

    def get_current_year(self):
        return datetime.now().year

    def get_price(self):
        year = datetime.now().year
        q1_start = date(year, 1, 1)
        q2_start = date(year, 4, 1)
        q3_start = date(year, 7, 1)
        q4_start = date(year, 10, 1)
        next_q1_start = date(year + 1, 1, 1)

        today = date.today()
        q1_frac = 1 - (today - q1_start).days / (q2_start - q1_start).days
        q2_frac = 1 - (today - q2_start).days / (q3_start - q2_start).days
        q3_frac = 1 - (today - q3_start).days / (q4_start - q3_start).days
        q4_frac = 1 - (today - q4_start).days / (next_q1_start - q4_start).days

        if not self.paid:
            if str(self.get_current_year()) < self.year:
                return self.location.price
            else:
                current_quarter = self.get_current_quarter()
                if current_quarter == 1:
                    if self.quarter == QuarterChoices.ONE:
                        return math.ceil(q1_frac * self.location.price * 100)
                    else:
                        return self.location.price
                elif current_quarter == 2:
                    if self.quarter == QuarterChoices.TWO:
                        return math.ceil(q2_frac * self.location.price * 100)
                    else:
                        return self.location.price
                elif current_quarter == 3:
                    if self.quarter == QuarterChoices.THREE:
                        return math.ceil(q3_frac * self.location.price * 100)
                    else:
                        return self.location.price
                else:
                    if self.quarter == QuarterChoices.FOUR:
                        return math.ceil(q4_frac * self.location.price * 100)
                    else:
                        return self.location.price

    def get_quarter_start(self):
        year = datetime.now().year
        q1_start = date(year, 1, 1)
        q2_start = date(year, 4, 1)
        q3_start = date(year, 7, 1)
        q4_start = date(year, 10, 1)
        today = date.today()
        if self.quarter == QuarterChoices.ONE:
            return q1_start if today < q1_start else today

        elif self.quarter == QuarterChoices.TWO:
            return q2_start if today < q2_start else today

        elif self.quarter == QuarterChoices.THREE:
            return q3_start if today < q3_start else today

        elif self.quarter == QuarterChoices.FOUR:
            return q4_start if today < q4_start else today

    def get_quarter_end(self):
        year = datetime.now().year
        q1_end = date(year, 4, 1) - timedelta(days=1)
        q2_end = date(year, 7, 1) - timedelta(days=1)
        q3_end = date(year, 10, 1) - timedelta(days=1)
        q4_end = date(year + 1, 1, 1) - timedelta(days=1)

        if self.quarter == QuarterChoices.ONE:
            return q1_end

        elif self.quarter == QuarterChoices.TWO:
            return q2_end

        elif self.quarter == QuarterChoices.THREE:
            return q3_end

        elif self.quarter == QuarterChoices.FOUR:
            return q4_end

    def get_created_duration(self):
        return (datetime.now() - self.time_created).total_seconds()

    def is_purgeable(self):
        return not self.paid and self.get_created_duration() > 1000

    # photo = models.FileField(
    #     verbose_name=_('Advertisement Photo'),
    #     null=True,
    #     storage=PublicMediaStorage()
    # )

    # remarks = models.TextField(
    #     verbose_name=_('Testimonial statment'),
    #     null=True
    # )

    # frozen = models.BooleanField(
    #     default=False,
    #     editable=False
    # )

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.time_created = timezone.now()
        return super().save(*args, **kwargs)
