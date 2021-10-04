from datetime import date


from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _


# from .validators import validate_links, validate_obscene_language

from accounts.models import PotentialEmployer, User
from maid.models import Maid, MaidResponsibility, MaidLanguage


from .constants import (
    PROPERTY_CHOICES, PROPERTY_2_ROOM_HDB, MAID_NATIONALITY_CHOICES,
    MAID_TYPE_CHOICES, NO_PREFERENCE, EnquiryStatusChoices
)
from .validators import validate_links



class GeneralEnquiry(models.Model):
    potential_employer = models.ForeignKey(
        PotentialEmployer,
        on_delete=models.CASCADE,
        related_name='general_enquiries',
        null=True
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100
    )

    mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=100
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        max_length=255
    )

    property_type = models.CharField(
        verbose_name=_('Type of Property'),
        choices=PROPERTY_CHOICES,
        default=PROPERTY_2_ROOM_HDB,
        max_length=7
    )

    maid_nationality = ArrayField(
        models.CharField(
            verbose_name=_('Maid\'s Nationality'),
            choices=MAID_NATIONALITY_CHOICES,
            default=NO_PREFERENCE,
            max_length=3
        )
    )

    maid_responsibility = models.ManyToManyField(
        MaidResponsibility,
        related_name='general_enquiries'
    )

    languages_spoken = models.ManyToManyField(
        MaidLanguage,
        related_name='general_enquiries'
    )

    maid_type = ArrayField(
        models.CharField(
            verbose_name=_('Type of maid'),
            choices=MAID_TYPE_CHOICES,
            default=NO_PREFERENCE,
            max_length=3
        )
    )

    no_of_family_members = models.IntegerField(
        verbose_name=_('Number of Family Members')
    )

    no_of_below_5 = models.IntegerField(
        verbose_name=_('Number of Children below 5')
    )

    remarks = models.CharField(
        verbose_name=_('Remarks'),
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

    date_published = models.DateField(
        null=True,
        editable=False
    )

    def get_maid_languages(self):
        txt = ''
        for i in self.languages_spoken.all():
            txt += str(i)
        return txt

    def get_maid_duties(self):
        txt = ''
        for i in self.maid_responsibility.all():
            txt += str(i)
        return txt

    def get_maid_nationalities(self):
        txt = ''
        for i in self.maid_nationality:
            txt += dict(MAID_NATIONALITY_CHOICES).get(i)
        return txt

    def get_maid_types(self):
        txt = ''
        for i in self.maid_type:
            txt += dict(MAID_TYPE_CHOICES).get(i)
        return txt

    @property
    def is_general_enquiry(self):
        return True

    def approve(self, user):
        self.approved = True
        self.last_modified = user
        self.date_published = date.today()
        self.save()

    def reject(self):
        # TODO: Add the rejection email mechanism
        self.delete()


class ShortlistedEnquiry(models.Model):
    potential_employer = models.ForeignKey(
        PotentialEmployer,
        on_delete=models.CASCADE,
        related_name='maid_enquiries'
    )

    maids = models.ManyToManyField(
        Maid,
        through='MaidShortlistedEnquiryIM',
        related_name='enquiries'
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100
    )

    mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=100
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        max_length=255
    )

    property_type = models.CharField(
        verbose_name=_('Type of Property'),
        choices=PROPERTY_CHOICES,
        default=PROPERTY_2_ROOM_HDB,
        max_length=7
    )

    no_of_family_members = models.IntegerField(
        verbose_name=_('Number of Family Members')
    )

    no_of_below_5 = models.IntegerField(
        verbose_name=_('Number of Children below 5')
    )

    remarks = models.CharField(
        verbose_name=_('Remarks'),
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

    date_published = models.DateField(
        null=True,
        editable=False
    )

    @property
    def is_shortlisted_enquiry(self):
        return True

    def approve(self, user):
        self.approved = True
        self.last_modified = user
        self.date_published = date.today()
        self.save()

    def reject(self):
        # TODO: Add the rejection email mechanism
        self.delete()

    def get_maids(self, agency_id):
        return self.maids.filter(
            agency__pk=agency_id
        )


class MaidShortlistedEnquiryIM(models.Model):
    maid = models.ForeignKey(
        Maid,
        related_name='maid_shortlist_enquiry_im',
        on_delete=models.CASCADE
    )

    shortlisted_enquiry = models.ForeignKey(
        ShortlistedEnquiry,
        related_name='maid_shortlist_enquiry_im',
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=1,
        choices=EnquiryStatusChoices.choices,
        default=EnquiryStatusChoices.OPEN
    )

    def set_status_accepted(self):
        self.status = EnquiryStatusChoices.ACCEPTED
        self.save()

    def set_status_rejected(self):
        self.status = EnquiryStatusChoices.REJECTED
        self.save()
