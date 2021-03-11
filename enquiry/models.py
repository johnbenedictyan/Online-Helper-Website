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
from agency.models import Agency
from maid.models import Maid, MaidResponsibility

# Imports from within the app
from .constants import *

# Utiliy Classes and Functions

# Start of Models
class GeneralEnquiry(models.Model):
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='general_enquiry',
        null=True
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
        default=PROPERTY_2_ROOM_HDB,
        max_length=7
    )

    maid_nationality = models.CharField(
        verbose_name=_('Maid\'s Nationality'),
        blank=False,
        choices=MAID_NATIONALITY_CHOICES,
        default=NO_PREFERENCE,
        max_length=3
    )

    maid_responsibility = models.ManyToManyField(
        MaidResponsibility,
        related_name='general_enquiry'
    )

    maid_type = models.CharField(
        verbose_name=_('Type of maid'),
        blank=False,
        choices=MAID_TYPE_CHOICES,
        default=NO_PREFERENCE,
        max_length=3
    )

    maid_age_group = models.CharField(
        verbose_name=_('Maid Age Group'),
        blank=False,
        choices=MAID_AGE_CHOICES,
        default=MAID_AGE_23_TO_29,
        max_length=8
    )

    rest_days = models.CharField(
        verbose_name=_('Number of Rest Days'),
        blank=False,
        choices=MAID_REST_DAY_CHOICES,
        default=MAID_REST_DAY_0,
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

    remarks = models.CharField(
        verbose_name=_('Remarks'),
        blank=False,
        max_length=3000
    )

    active = models.BooleanField(
        editable=False,
        default=True
    )
 
class AgencyEnquiry(models.Model):
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='enquiry'
    )
    
    name = models.CharField(
        verbose_name=_('Name'),
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

    maid_nationality = models.CharField(
        verbose_name=_('Maid\'s Nationality'),
        blank=False,
        choices=MAID_NATIONALITY_CHOICES,
        default=NO_PREFERENCE,
        max_length=3
    )

    maid_responsibility = models.ManyToManyField(
        MaidResponsibility,
        related_name='agency_enquiry'
    )

    maid_type = models.CharField(
        verbose_name=_('Type of maid'),
        blank=False,
        choices=MAID_TYPE_CHOICES,
        default=NO_PREFERENCE,
        max_length=3
    )

    maid_age_group = models.CharField(
        verbose_name=_('Maid Age Group'),
        blank=False,
        choices=MAID_AGE_CHOICES,
        default=MAID_AGE_23_TO_29,
        max_length=8
    )
    
    remarks = models.TextField(
        verbose_name=_('Remarks'),
        blank=False
    )
    
class MaidEnquiry(models.Model):
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='maid_enquiry'
    )
    
    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='enquiry'
    )
    
    remarks = models.TextField(
        verbose_name=_('Remarks'),
        blank=False
    )