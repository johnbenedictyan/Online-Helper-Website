# Imports from python

# Imports from django
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

# Imports from project

# Imports from other apps
from accounts.models import Employer
from maid.models import MaidResponsibility

# Imports from within the app

# Utiliy Classes and Functions

# Start of Models
class Enquiry(models.Model):
    # Settings

    ## General
    NO_PREFERENCE = 'ALL'
    OTHERS        = 'OTH'

    ## Maid Age
    MAID_AGE_23_TO_29 = '23-29'
    MAID_AGE_30_TO_39 = '30-39'
    MAID_AGE_40_TO_49 = '40-49'
    MAID_AGE_ABOVE_50 = 'above 50'

    ## Maid Nationality
    MAID_NATIONALITY_CAMBODIAN  = 'KHM'
    MAID_NATIONALITY_FILIPINO   = 'PHL'
    MAID_NATIONALITY_INDIAN     = 'IND'
    MAID_NATIONALITY_INDONESIAN = 'IDN'
    MAID_NATIONALITY_MYANMARESE = 'MMR'
    MAID_NATIONALITY_SRI_LANKAN = 'LKA'
    
    ## Maid Rest Days
    MAID_REST_DAY_0 = '0RD'
    MAID_REST_DAY_1 = '1RD'
    MAID_REST_DAY_2 = '2RD'
    MAID_REST_DAY_3 = '3RD'
    MAID_REST_DAY_4 = '4RD'

    ## Maid Type
    MAID_TYPE_NO_EXPERIENCE       = 'NEW'
    MAID_TYPE_TRANSFER            = 'TRA'
    MAID_TYPE_SG_EXPERIENCE       = 'SGE'
    MAID_TYPE_OVERSEAS_EXPERIENCE = 'OVE'

    ## Property Type
    PROPERTY_2_ROOM_HDB               = '2RMHDB'
    PROPERTY_3_ROOM_HDB               = '3RMHDB'
    PROPERTY_4_ROOM_HDB               = '4RMHDB'
    PROPERTY_5_ROOM_HDB               = '5RMHDB'
    PROPERTY_EXECUTIVE_MAISONETTE_HDB = 'E/MHDB'
    PROPERTY_CONDOMINIUM              = 'CONDO'
    PROPERTY_CONDOMINIUM_PENTHOUSE    = 'CONDOP'
    PROPERTY_TERRACE                  = 'TERRACE'
    PROPERTY_SEMI_DETACHED            = 'SEMI-D'
    PROPERTY_BUNGALOW                 = 'BUNGLO'
    PROPERTY_OTHERS                   = 'OTH'
    
    MAID_NATIONALITY_CHOICES = (
        (NO_PREFERENCE, _('No preference')),
        (MAID_NATIONALITY_CAMBODIAN, _('Cambodian')),
        (MAID_NATIONALITY_FILIPINO, _('Filipino')),
        (MAID_NATIONALITY_INDIAN, _('Indian')),
        (MAID_NATIONALITY_INDONESIAN, _('Indonesian')),
        (MAID_NATIONALITY_MYANMARESE, _('Myanmarese')),
        (MAID_NATIONALITY_SRI_LANKAN, _('Sri Lankan')),
        (OTHERS, _('Others'))
    )

    MAID_TYPE_CHOICES = (
        (NO_PREFERENCE, _('No preference')),
        (MAID_TYPE_NO_EXPERIENCE, _('No Experience')),
        (MAID_TYPE_TRANSFER, _('Transfer')),
        (MAID_TYPE_SG_EXPERIENCE, _('Singapore Experience')),
        (MAID_TYPE_OVERSEAS_EXPERIENCE, _('Overseas Experience'))
    )

    MAID_AGE_CHOICES = (
        (MAID_AGE_23_TO_29, _('23-29')),
        (MAID_AGE_30_TO_39, _('30-39')),
        (MAID_AGE_40_TO_49, _('40-49')),
        (MAID_AGE_ABOVE_50, _('Above 50'))
    )
    
    PROPERTY_CHOICES = (
        (PROPERTY_2_ROOM_HDB, _('2-Room HDB')),
        (PROPERTY_3_ROOM_HDB, _('3-Room HDB')),
        (PROPERTY_4_ROOM_HDB, _('4-Room HDB')),
        (PROPERTY_5_ROOM_HDB, _('5-Room HDB')),
        (PROPERTY_EXECUTIVE_MAISONETTE_HDB, _('Executive/Maisonette HDB')),
        (PROPERTY_CONDOMINIUM, _('Condominium')),
        (PROPERTY_CONDOMINIUM_PENTHOUSE, _('Condominium Penthouse')),
        (PROPERTY_TERRACE, _('Terrace')),
        (PROPERTY_SEMI_DETACHED, _('Semi-Detached')),
        (PROPERTY_BUNGALOW, _('Bungalow')),
        (PROPERTY_OTHERS, _('Others')),
    )
    MAID_REST_DAY_CHOICES = (
        (MAID_REST_DAY_0, _('0 Rest Days Per Month')),
        (MAID_REST_DAY_1, _('1 Rest Days Per Month')),
        (MAID_REST_DAY_2, _('2 Rest Days Per Month')),
        (MAID_REST_DAY_3, _('3 Rest Days Per Month')),
        (MAID_REST_DAY_4, _('4 Rest Days Per Month'))
    )

    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='employer'
    )
    
    first_name = models.CharField(
        verbose_name=_('First Name'),
        blank=False,
        max_length=100
    )

    last_name = models.CharField(
        verbose_name=_('Last Name'),
        blank=False,
        max_length=100
    )

    contact_number = models.CharField(
        verbose_name=_('Contact Number'),
        blank=False,
        max_length=100
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        blank=False,
        max_length=255
    )

    property_type = models.CharField(
        verbose_name=_('Type of Property'),
        blank=False,
        choices=PROPERTY_CHOICES,
        max_length=7
    )

    maid_nationality = models.CharField(
        verbose_name=_('Maid\'s Nationality'),
        blank=False,
        choices=MAID_NATIONALITY_CHOICES,
        max_length=3
    )

    maid_responsibility = models.ManyToManyField(
        MaidResponsibility,
        related_name='enquiry'
    )

    maid_type = models.CharField(
        verbose_name=_('Type of maid'),
        blank=False,
        choices=MAID_TYPE_CHOICES,
        max_length=3
    )

    maid_age_group = models.CharField(
        verbose_name=_('Maid Age Group'),
        blank=False,
        choices=MAID_AGE_CHOICES,
        max_length=8
    )

    rest_days = models.CharField(
        verbose_name=_('Number of Rest Days'),
        blank=False,
        choices=MAID_REST_DAY_CHOICES,
        max_length=3
    )
    
    no_of_family_members = models.IntegerField(
        verbose_name=_('Number of Family Members'),
        blank=False
    )

    no_of_below_12 = models.IntegerField(
        verbose_name=_('Number of Children below 12'),
        blank=False
    )

    no_of_babies = models.IntegerField(
        verbose_name=_('Number of Babies'),
        blank=False
    )

    remarks = models.TextField(
        verbose_name=_('Remarks'),
        blank=False
    )

    active = models.BooleanField(
        editable=False,
        default=True
    )