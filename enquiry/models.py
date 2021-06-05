# Imports from python

# Imports from django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Imports from project

# Imports from other apps
from accounts.models import PotentialEmployer, User
from agency.models import Agency
from maid.models import Maid, MaidResponsibility, MaidLanguage

# Imports from within the app
from .constants import *
from .validators import validate_links
# from .validators import validate_links, validate_obscene_language

# Utiliy Classes and Functions

# Start of Models
class GeneralEnquiry(models.Model):
    potential_employer = models.ForeignKey(
        PotentialEmployer,
        on_delete=models.CASCADE,
        related_name='general_enquiries',
        null=True
    )
    
    name = models.CharField(
        verbose_name=_('Name'),
        blank=False,
        max_length=100
    )

    mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
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
        related_name='general_enquiries'
    )

    languages_spoken = models.ManyToManyField(
        MaidLanguage,
        related_name='general_enquiries'
    )

    maid_type = models.CharField(
        verbose_name=_('Type of maid'),
        blank=False,
        choices=MAID_TYPE_CHOICES,
        default=NO_PREFERENCE,
        max_length=3
    )

    no_of_family_members = models.IntegerField(
        verbose_name=_('Number of Family Members'),
        blank=False
    )

    no_of_below_5 = models.IntegerField(
        verbose_name=_('Number of Children below 5'),
        blank=False
    )

    remarks = models.CharField(
        verbose_name=_('Remarks'),
        blank=False,
        max_length=3000,
        validators=[
            validate_links, 
            # validate_obscene_language
        ]
    )

    active = models.BooleanField(
        editable=False,
        default=True
    )

    approved = models.BooleanField(
        editable=False,
        default=False
    )

    last_modified = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='last_modified_general_enquiries',
        null=True
    )

    # date_published = models.DateField(
    #     auto_created=True,
    #     editable=False
    # )

    def display_languages(self):
        txt = ''
        for i in self.languages_spoken.all():
            txt+=str(i)
        return txt

    def display_duties(self):
        txt = ''
        for i in self.maid_responsibility.all():
            txt+=str(i)
        return txt
 
class ShortlistedEnquiry(models.Model):
    potential_employer = models.ForeignKey(
        PotentialEmployer,
        on_delete=models.CASCADE,
        related_name='maid_enquiries'
    )
    
    maids = models.ManyToManyField(
        Maid,
        related_name='enquiries'
    )
    
    name = models.CharField(
        verbose_name=_('Name'),
        blank=False,
        max_length=100
    )

    mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
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

    no_of_family_members = models.IntegerField(
        verbose_name=_('Number of Family Members'),
        blank=False
    )

    no_of_below_5 = models.IntegerField(
        verbose_name=_('Number of Children below 5'),
        blank=False
    )

    remarks = models.CharField(
        verbose_name=_('Remarks'),
        blank=False,
        max_length=3000,
        validators=[
            validate_links, 
            # validate_obscene_language
        ]
    )

    active = models.BooleanField(
        editable=False,
        default=True
    )

    approved = models.BooleanField(
        editable=False,
        default=False
    )

    last_modified = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='last_modified_maid_enquiries',
        null=True
    )

    # date_published = models.DateField(
    #     auto_created=True,
    #     editable=False
    # )
