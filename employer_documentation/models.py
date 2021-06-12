# Imports from python
import os
import uuid
import secrets
from decimal import Decimal, ROUND_HALF_UP

# Imports from django
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.utils.translation import ugettext_lazy as _

# Imports from other apps
from onlinemaid.constants import TrueFalseChoices
from onlinemaid.helper_functions import decrypt_string
from onlinemaid.storage_backends import EmployerDocumentationStorage
from agency.models import AgencyEmployee
from maid.models import Maid
from maid.constants import FullNationsChoices

# Same app
from . import constants as ed_constants
from .fields import CustomMoneyDecimalField

# Utiliy Classes and Functions
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, filename, max_length=100):
        if self.exists(filename):
            os.remove(os.path.join(self.location, filename))
        return filename

def generate_joborder_path(instance, filename):
    relative_path = 'archive/' + str(instance.employer_doc.pk)
    # return the whole path to the file
    return os.path.join(relative_path, 'f07_job_order.pdf')

def generate_archive_path(instance, filename):
    # filename parameter is passed from view in format:
    # 'level_1_pk:name_of_file.pdf'
    filename_split = filename.split(':')
    level_1_pk = filename_split[0]
    relative_path = 'archive/' + level_1_pk
    # return the whole path to the file
    return os.path.join(relative_path, filename_split[-1])


# Start of Models

# Employer e-Documentation Models
class Employer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    applicant_type = models.CharField(
        verbose_name=_("Type of Applicant"),
        max_length=6,
        choices=ed_constants.EmployerTypeOfApplicantChoices.choices,
        default=ed_constants.EmployerTypeOfApplicantChoices.SINGLE,
    )

    household_details_required = models.BooleanField(
        verbose_name=_('Applicable for subsidised levy?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            If yes, please fill in household details section
        '''),
    )

    agency_employee = models.ForeignKey(
        AgencyEmployee,
        verbose_name=_('Assigned EA Personnel'),
        on_delete=models.RESTRICT,
    )

    # Employer Information
    employer_name = models.CharField(
        verbose_name=_('Employer Name'),
        max_length=40,
    )

    employer_gender = models.CharField(
        verbose_name=_("Employer gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
    )

    employer_mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$', # Singapore mobile numbers
                message=_('Please enter a valid mobile number')
            )
        ],
    )

    employer_home_number = models.CharField(
        verbose_name=_('Home Tel Number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[6][0-9]{7}$', # Singapore landline numbers
                message=_('Please enter a valid home telephone number')
            )
        ],
    )

    employer_email = models.EmailField(
        verbose_name=_('Email Address')
    )

    employer_address_1 = models.CharField(
        verbose_name=_('Address Line 1'),
        max_length=100,
    )

    employer_address_2 = models.CharField(
        verbose_name=_('Address Line 2'),
        max_length=50,
        blank=True,
        null=True,
    )

    employer_post_code = models.CharField(
        verbose_name=_('Postal Code'),
        max_length=25,
    )

    employer_date_of_birth = models.DateField(
        verbose_name=_('Employer date of birth'),
    )

    employer_nationality = models.CharField(
        verbose_name=_("Employer nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )

    employer_residential_status = models.CharField(
        verbose_name=_("Employer residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
    )

    employer_nric_num = models.BinaryField(
        verbose_name=_('Employer NRIC'),
        editable=True,
        blank=True,
        null=True,
    )

    employer_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )

    employer_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )

    employer_fin_num = models.BinaryField(
        verbose_name=_('Employer FIN'),
        editable=True,
        blank=True,
        null=True,
    )

    employer_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )

    employer_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )

    employer_passport_num = models.BinaryField(
        verbose_name=_('Employer passport'),
        editable=True,
        blank=True,
        null=True,
    )

    employer_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )

    employer_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )

    employer_passport_date = models.DateField(
        verbose_name=_('Employer passport expiry date'),
        blank=True,
        null=True,
    )

    employer_marital_status = models.CharField(
        verbose_name=_("Employer marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
        blank=True,
        null=True,
    )

    employer_marriage_sg_registered = models.BooleanField(
        verbose_name=_('Employer marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Employer's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )

    def get_employer_nric_full(self):
        return decrypt_string(
            self.employer_nric_num,
            settings.ENCRYPTION_KEY,
            self.employer_nric_nonce,
            self.employer_nric_tag,
        )
    
    def get_employer_nric_partial(self, padded=True):
        plaintext = self.get_employer_nric_full()
        if padded == True:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

    def get_employer_fin_full(self):
        return decrypt_string(
            self.employer_fin_num,
            settings.ENCRYPTION_KEY,
            self.employer_fin_nonce,
            self.employer_fin_tag,
        )
    
    def get_employer_fin_partial(self, padded=True):
        plaintext = self.get_employer_fin_full()
        if padded == True:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

    def get_employer_passport(self):
        return decrypt_string(
            self.employer_passport_num,
            settings.ENCRYPTION_KEY,
            self.employer_passport_nonce,
            self.employer_passport_tag,
        )

    def get_spouse_nric_full(self):
        return decrypt_string(
            self.spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.spouse_nric_nonce,
            self.spouse_nric_tag,
        )
    
    def get_spouse_fin(self):
        return decrypt_string(
            self.spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.spouse_fin_nonce,
            self.spouse_fin_tag,
        )

    def get_spouse_passport(self):
        return decrypt_string(
            self.spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.spouse_passport_nonce,
            self.spouse_passport_tag,
        )

    def mobile_partial_sg(self):
        return '+65 ' + self.employer_mobile_number[:4] + ' ' + 'x'*4

    def get_email_partial(self):
        return self.employer_email[:3] + '_'*8 + self.employer_email[-3:]

    ## Employer Spouse
    spouse_name = models.CharField(
        verbose_name=_("Spouse's Name"),
        max_length=40,
        blank=True,
        null=True,
        default=None,
    )
    
    spouse_gender = models.CharField(
        verbose_name=_("Spouse's gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    
    spouse_date_of_birth = models.DateField(
        verbose_name=_("Spouse's date of birth"),
        blank=True,
        null=True,
    )
    
    spouse_nationality = models.CharField(
        verbose_name=_("Spouse's nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    
    spouse_residential_status = models.CharField(
        verbose_name=_("Spouse's residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    
    spouse_nric_num = models.BinaryField(
        verbose_name=_("Spouse's NRIC"),
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_fin_num = models.BinaryField(
        verbose_name=_("Spouse's FIN"),
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_passport_num = models.BinaryField(
        verbose_name=_("Spouse's Passport No"),
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    spouse_passport_date = models.DateField(
        verbose_name=_("Spouse's Passport Expiry Date"),
        blank=True,
        null=True,
    )

    def get_employer_spouse_nric_full(self):
        return decrypt_string(
            self.spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.spouse_nric_nonce,
            self.spouse_nric_tag,
        )

    def get_employer_spouse_fin_full(self):
        return decrypt_string(
            self.spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.spouse_fin_nonce,
            self.spouse_fin_tag,
        )

    def get_employer_spouse_passport_full(self):
        return decrypt_string(
            self.spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.spouse_passport_nonce,
            self.spouse_passport_tag,
        )

    #Utility Functions
    def has_income_obj(self):
        try:
            income_obj = self.rn_income_employer
        except ObjectDoesNotExist:
            pass
        else:
            return income_obj

    def has_sponsor_obj(self):
        try:
            sponsor_obj = self.rn_sponsor_employer
        except ObjectDoesNotExist:
            pass
        else:
            return sponsor_obj

    def has_joint_applicant_obj(self):
        try:
            joint_applicant_obj = self.rn_ja_employer
        except ObjectDoesNotExist:
            pass
        else:
            return joint_applicant_obj

    def __str__(self):
        return self.employer_name

## Sponsors
class EmployerSponsor(models.Model):
    employer = models.OneToOneField(
        Employer,
        on_delete=models.CASCADE,
        related_name='rn_sponsor_employer'
    )
    
    # Sponsor 1 details
    sponsor_1_relationship = models.CharField(
        verbose_name=_("Sponsor 1 relationship with Employer"),
        max_length=30,
        choices=ed_constants.RelationshipChoices.choices,
        default=ed_constants.RelationshipChoices.DAUGHTER,
    )
    sponsor_1_name = models.CharField(
        verbose_name=_('Sponsor 1 Name'),
        max_length=40,
    )
    sponsor_1_gender = models.CharField(
        verbose_name=_("Sponsor 1 gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
    )
    sponsor_1_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 1 date of birth'),
    )
    sponsor_1_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 1 NRIC'),
        editable=True,
    )
    sponsor_1_nric_nonce = models.BinaryField(
        editable=True,
    )
    sponsor_1_nric_tag = models.BinaryField(
        editable=True,
    )
    sponsor_1_nationality = models.CharField(
        verbose_name=_("Sponsor 1 nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
    )
    sponsor_1_residential_status = models.CharField(
        verbose_name=_("Sponsor 1 residential status"),
        max_length=2,
        choices=ed_constants.ResidentialStatusPartialChoices.choices,
        default=ed_constants.ResidentialStatusPartialChoices.SC,
    )
    sponsor_1_mobile_number = models.CharField(
        verbose_name=_('Sponsor 1 mobile number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$', # Singapore mobile numbers
                message=_('Please enter a valid contact number')
            )
        ],
    )
    sponsor_1_email = models.EmailField(
        verbose_name=_('Sponsor 1 email address'),
    )
    sponsor_1_address_1 = models.CharField(
        verbose_name=_('Sponsor 1 Address Line 1'),
        max_length=100,
    )
    sponsor_1_address_2 = models.CharField(
        verbose_name=_('Sponsor 1 Address Line 2'),
        max_length=50,
        blank=True,
        null=True,
    )
    sponsor_1_post_code = models.CharField(
        verbose_name=_('Sponsor 1 Postal Code'),
        max_length=25,
    )
    sponsor_1_marital_status = models.CharField(
        verbose_name=_("Sponsor 1 marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
    )

    # Sponsor 1 spouse details
    sponsor_1_marriage_sg_registered = models.BooleanField(
        verbose_name=_('Sponsor 1 marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Sponsor 1's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )
    sponsor_1_spouse_name = models.CharField(
        verbose_name=_('Sponsor 1 spouse name'),
        max_length=40,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_gender = models.CharField(
        verbose_name=_("Sponsor 1 spouse gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 1 spouse date of birth'),
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nationality = models.CharField(
        verbose_name=_("Sponsor 1 spouse nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_residential_status = models.CharField(
        verbose_name=_("Sponsor 1 spouse residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 1 spouse NRIC'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_fin_num = models.BinaryField(
        verbose_name=_('Sponsor 1 spouse FIN'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_num = models.BinaryField(
        verbose_name=_('Sponsor 1 spouse passport'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_date = models.DateField(
        verbose_name=_('Sponsor 1 spouse passport expiry date'),
        blank=True,
        null=True,
    )

    # Sponsor required?
    sponsor_2_required = models.BooleanField(
        verbose_name=_('Do you need to add Sponsor 2?'),
        default=False,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
    )

    # Sponsor 2 details
    sponsor_2_relationship = models.CharField(
        verbose_name=_("Sponsor 2 relationship with Employer"),
        max_length=30,
        choices=ed_constants.RelationshipChoices.choices,
        default=ed_constants.RelationshipChoices.DAUGHTER,
        blank=True,
        null=True,
    )
    sponsor_2_name = models.CharField(
        verbose_name=_('Sponsor 2 Name'),
        max_length=40,
        blank=True,
        null=True,
    )
    sponsor_2_gender = models.CharField(
        verbose_name=_("Sponsor 2 gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    sponsor_2_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 2 date of birth'),
        blank=True,
        null=True,
    )
    sponsor_2_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 2 NRIC'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_nationality = models.CharField(
        verbose_name=_("Sponsor 2 nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    sponsor_2_residential_status = models.CharField(
        verbose_name=_("Sponsor 2 residential status"),
        max_length=2,
        choices=ed_constants.ResidentialStatusPartialChoices.choices,
        default=ed_constants.ResidentialStatusPartialChoices.SC,
        blank=True,
        null=True,
    )
    sponsor_2_mobile_number = models.CharField(
        verbose_name=_('Sponsor 2 mobile number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$', # Singapore mobile numbers
                message=_('Please enter a valid contact number')
            )
        ],
        blank=True,
        null=True,
    )
    sponsor_2_email = models.EmailField(
        verbose_name=_('Sponsor 2 email address'),
        blank=True,
        null=True,
    )
    sponsor_2_address_1 = models.CharField(
        verbose_name=_('Sponsor 2 Address Line 1'),
        max_length=100,
        blank=True,
        null=True,
    )
    sponsor_2_address_2 = models.CharField(
        verbose_name=_('Sponsor 2 Address Line 2'),
        max_length=50,
        blank=True,
        null=True,
    )
    sponsor_2_post_code = models.CharField(
        verbose_name=_('Sponsor 2 Postal Code'),
        max_length=25,
        blank=True,
        null=True,
    )
    sponsor_2_marital_status = models.CharField(
        verbose_name=_("Sponsor 2 marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
        blank=True,
        null=True,
    )
    sponsor_2_marriage_sg_registered = models.BooleanField(
        verbose_name=_('Sponsor 2 marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Sponsor 2's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )

    # Sponsor 2 spouse details
    sponsor_2_spouse_name = models.CharField(
        verbose_name=_('Sponsor 2 spouse name'),
        max_length=40,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_gender = models.CharField(
        verbose_name=_("Sponsor 2 spouse gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 2 spouse date of birth'),
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nationality = models.CharField(
        verbose_name=_("Sponsor 2 spouse nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_residential_status = models.CharField(
        verbose_name=_("Sponsor 2 spouse residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 2 spouse NRIC'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_fin_num = models.BinaryField(
        verbose_name=_('Sponsor 2 spouse FIN'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_num = models.BinaryField(
        verbose_name=_('Sponsor 2 spouse passport'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_date = models.DateField(
        verbose_name=_('Sponsor 2 spouse passport expiry date'),
        blank=True,
        null=True,
    )

    def get_sponsor_1_nric_full(self):
        return decrypt_string(
            self.sponsor_1_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_nric_nonce,
            self.sponsor_1_nric_tag,
        )

    def get_sponsor_1_spouse_nric_full(self):
        return decrypt_string(
            self.sponsor_1_spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_spouse_nric_nonce,
            self.sponsor_1_spouse_nric_tag,
        )

    def get_sponsor_1_spouse_fin_full(self):
        return decrypt_string(
            self.sponsor_1_spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_spouse_fin_nonce,
            self.sponsor_1_spouse_fin_tag,
        )

    def get_sponsor_1_spouse_passport_full(self):
        return decrypt_string(
            self.sponsor_1_spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_spouse_passport_nonce,
            self.sponsor_1_spouse_passport_tag,
        )
    
    def get_sponsor_2_nric_full(self):
        return decrypt_string(
            self.sponsor_2_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_nric_nonce,
            self.sponsor_2_nric_tag,
        )

    def get_sponsor_2_spouse_nric_full(self):
        return decrypt_string(
            self.sponsor_2_spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_spouse_nric_nonce,
            self.sponsor_2_spouse_nric_tag,
        )

    def get_sponsor_2_spouse_fin_full(self):
        return decrypt_string(
            self.sponsor_2_spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_spouse_fin_nonce,
            self.sponsor_2_spouse_fin_tag,
        )

    def get_sponsor_2_spouse_passport_full(self):
        return decrypt_string(
            self.sponsor_2_spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_spouse_passport_nonce,
            self.sponsor_2_spouse_passport_tag,
        )

## Joint Applicants
class EmployerJointApplicant(models.Model):
    employer = models.OneToOneField(
        Employer,
        on_delete=models.CASCADE,
        related_name='rn_ja_employer'
    )
    joint_applicant_relationship = models.CharField(
        verbose_name=_("Joint applicant's relationship with Employer"),
        max_length=30,
        choices=ed_constants.RelationshipChoices.choices,
        default=ed_constants.RelationshipChoices.DAUGHTER,
    )
    joint_applicant_name = models.CharField(
        verbose_name=_("Joint applicant's Name"),
        max_length=40,
    )
    joint_applicant_gender = models.CharField(
        verbose_name=_("Joint applicant's gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
    )
    joint_applicant_date_of_birth = models.DateField(
        verbose_name=_("Joint applicant's date of birth"),
    )
    joint_applicant_nric_num = models.BinaryField(
        verbose_name=_('Joint applicant NRIC'),
        editable=True,
    )
    joint_applicant_nric_nonce = models.BinaryField(
        editable=True,
    )
    joint_applicant_nric_tag = models.BinaryField(
        editable=True,
    )
    joint_applicant_nationality = models.CharField(
        verbose_name=_("Joint applicant's nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
    )
    joint_applicant_residential_status = models.CharField(
        verbose_name=_("Joint applicant's residential status"),
        max_length=2,
        choices=ed_constants.ResidentialStatusPartialChoices.choices,
        default=ed_constants.ResidentialStatusPartialChoices.SC,
    )
    joint_applicant_address_1 = models.CharField(
        verbose_name=_("Joint applicant's Address Line 1"),
        max_length=100,
    )
    joint_applicant_address_2 = models.CharField(
        verbose_name=_("Joint applicant's Address Line 2"),
        max_length=50,
        blank=True,
        null=True,
    )
    joint_applicant_post_code = models.CharField(
        verbose_name=_("Joint applicant's Postal Code"),
        max_length=25,
    )
    joint_applicant_marital_status = models.CharField(
        verbose_name=_("Joint applicant's marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
    )
    joint_applicant_marriage_sg_registered = models.BooleanField(
        verbose_name=_("Joint applicant's marriage registered in SG?"),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Joint applicant's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )

    # Joint applicant's spouse details
    joint_applicant_spouse_name = models.CharField(
        verbose_name=_("Joint applicant's spouse name"),
        max_length=40,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_gender = models.CharField(
        verbose_name=_("Joint applicant's spouse gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_date_of_birth = models.DateField(
        verbose_name=_("Joint applicant's spouse date of birth"),
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nationality = models.CharField(
        verbose_name=_("Joint applicant's spouse nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_residential_status = models.CharField(
        verbose_name=_("Joint applicant's spouse residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nric_num = models.BinaryField(
        verbose_name=_("Joint applicant's spouse NRIC"),
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_fin_num = models.BinaryField(
        verbose_name=_("Joint applicant's spouse FIN"),
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_num = models.BinaryField(
        verbose_name=_("Joint applicant's spouse passport"),
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_date = models.DateField(
        verbose_name=_("Joint applicant's spouse passport expiry date"),
        blank=True,
        null=True,
    )

    def get_joint_applicant_nric_full(self):
        return decrypt_string(
            self.joint_applicant_nric_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_nric_nonce,
            self.joint_applicant_nric_tag,
        )
    
    def get_joint_applicant_spouse_nric_full(self):
        return decrypt_string(
            self.joint_applicant_spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_spouse_nric_nonce,
            self.joint_applicant_spouse_nric_tag,
        )

    def get_joint_applicant_spouse_fin_full(self):
        return decrypt_string(
            self.joint_applicant_spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_spouse_fin_nonce,
            self.joint_applicant_spouse_fin_tag,
        )

    def get_joint_applicant_spouse_passport_full(self):
        return decrypt_string(
            self.joint_applicant_spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_spouse_passport_nonce,
            self.joint_applicant_spouse_passport_tag,
        )

class EmployerIncome(models.Model):
    employer = models.OneToOneField(
        Employer,
        verbose_name=_("Name of Employer"),
        on_delete=models.CASCADE,
        related_name="rn_income_employer",
    )
    # Income Details
    worked_in_sg = models.BooleanField(
        verbose_name=_('Have you worked in Singapore for the last 2 Years?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
    )
    monthly_income = models.PositiveSmallIntegerField(
        verbose_name=_("Monthly Income"),
        choices=ed_constants.IncomeChoices.choices,
        default=ed_constants.IncomeChoices.INCOME_3,
    )

class EmployerHousehold(models.Model):
    employer = models.ForeignKey(
        Employer,
        verbose_name=_("Name of Employer"),
        on_delete=models.CASCADE,
        related_name="rn_household_employer",
    )
    # Household Details
    household_name = models.CharField(
        verbose_name=_("Household member's name"),
        max_length=40,
    )
    household_id_type = models.CharField(
        verbose_name=_("Household member ID type"),
        max_length=8,
        choices=ed_constants.HouseholdIdTypeChoices.choices,
        # default=ed_constants.HouseholdIdTypeChoices.NRIC,
    )
    household_id_num = models.BinaryField(
        verbose_name=_("Household member's ID number"),
        editable=True,
    )
    household_id_nonce = models.BinaryField(
        editable=True,
    )
    household_id_tag = models.BinaryField(
        editable=True,
    )
    household_date_of_birth = models.DateField(
        verbose_name=_("Household member's date of birth"),
    )
    household_relationship = models.CharField(
        verbose_name=_("Household member's relationship with Employer"),
        max_length=30,
        choices=ed_constants.RelationshipChoices.choices,
        # default=ed_constants.RelationshipChoices.DAUGHTER,
    )

    def get_household_id_full(self):
        return decrypt_string(
            self.household_id_num,
            settings.ENCRYPTION_KEY,
            self.household_id_nonce,
            self.household_id_tag,
        )

class EmployerDoc(models.Model):
    # Auto fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    version = models.PositiveSmallIntegerField(
        editable=False,
        default=0,
    )

    # User input fields
    case_ref_no = models.CharField(
        verbose_name=_("Case Reference Number"),
        max_length=20,
        unique=True,
    )
    agreement_date = models.DateField(
        verbose_name=_("Contract Date"),
    )
    employer = models.ForeignKey(
        Employer,
        verbose_name=_("Name of Employer"),
        on_delete=models.CASCADE,
        related_name="rn_ed_employer",
    )
    fdw = models.ForeignKey(
        Maid,
        verbose_name=_("Name of FDW"),
        on_delete=models.RESTRICT,
    )
    fdw_salary = CustomMoneyDecimalField(
        verbose_name=_("FDW Basic Salary"),
        help_text=_("FDW monthly salary per contract"),
    )
    fdw_loan = CustomMoneyDecimalField(
        verbose_name=_("FDW Loan Amount"),
        help_text=_("FDW loan amount per contract"),
    )
    fdw_off_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("FDW No. of off-days per month"),
        choices=ed_constants.DayChoices.choices[0:5],
        default=4,
        help_text=_("FDW off-days a month per contract"),
    )
    fdw_monthly_loan_repayment = CustomMoneyDecimalField(
        verbose_name=_("FDW Monthly Loan Repayment"),
        help_text=_("Should be less than basic salary"),
    )
    fdw_off_day_of_week = models.PositiveSmallIntegerField(
        verbose_name=_("FDW Off Day Day of Week"),
        choices=ed_constants.DayOfWeekChoices.choices,
        default=ed_constants.DayOfWeekChoices.SUN
    )

    def save(self, *args, **kwargs):
        # Auto-increment document version number on every save
        self.version += 1
        super().save(*args, **kwargs)

        # Create related CaseStatus object if it does not exist
        if not hasattr(self, 'rn_casestatus_ed'):
            CaseStatus.objects.create(employer_doc=self)
        
        # Create related CaseSignature object if it does not exist
        if not hasattr(self, 'rn_signatures_ed'):
            CaseSignature.objects.create(employer_doc=self)

    def get_version(self):
        return str(self.version).zfill(4)

    def per_off_day_compensation(self):
        return Decimal(self.fdw_salary/ed_constants.NUMBER_OF_WORK_DAYS_IN_MONTH).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def fdw_off_day_of_week_display(self):
        if int(self.fdw_off_day_of_week) == ed_constants.DayOfWeekChoices.MON:
            return _('Monday')
        elif int(self.fdw_off_day_of_week) == ed_constants.DayOfWeekChoices.TUE:
            return _('Tuesday')
        elif int(self.fdw_off_day_of_week) == ed_constants.DayOfWeekChoices.WED:
            return _('Wednesday')
        elif int(self.fdw_off_day_of_week) == ed_constants.DayOfWeekChoices.THU:
            return _('Thursday')
        elif int(self.fdw_off_day_of_week) == ed_constants.DayOfWeekChoices.FRI:
            return _('Friday')
        elif int(self.fdw_off_day_of_week) == ed_constants.DayOfWeekChoices.SAT:
            return _('Saturday')
        else:
            return _('Sunday')

    def archive(self):
        ArchivedDoc.objects.get_or_create(
            id=self.id,
            defaults={
                'applicant_type':self.employer.applicant_type,
                'agency_name':self.employer.agency_employee.agency.name,
                'agency_license_no':self.employer.agency_employee.agency.license_number,
                'agency_address_line_1':self.employer.agency_employee.agency.get_main_branch().address_1,
                'agency_address_line_2':self.employer.agency_employee.agency.get_main_branch().address_2,
                'agency_postal_code':self.employer.agency_employee.agency.get_main_branch().postal_code,
                'agency_employee_name':self.employer.agency_employee.name,
                'agency_employee_ea_personnel_number':self.employer.agency_employee.ea_personnel_number,
                'maid_name':self.fdw.name,
                'maid_nationality':self.fdw.country_of_origin,
                'maid_passport_number':self.fdw.passport_number,
                'maid_passport_number_nonce':self.fdw.nonce,
                'maid_passport_number_tag':self.fdw.tag,
                'maid_work_permit_number':self.fdw.work_permit,
                'employer_name':self.employer.employer_name,
                'employer_gender':self.employer.employer_gender,
                'employer_mobile_number':self.employer.employer_mobile_number,
                'employer_home_number':self.employer.employer_home_number,
                'employer_email':self.employer.employer_email,
                'employer_address_1':self.employer.employer_address_1,
                'employer_address_2':self.employer.employer_address_2,
                'employer_post_code':self.employer.employer_post_code,
                'employer_date_of_birth':self.employer.employer_date_of_birth,
                'employer_nationality':self.employer.employer_nationality,
                'employer_residential_status':self.employer.employer_residential_status,
                'employer_nric_num':self.employer.employer_nric_num,
                'employer_nric_nonce':self.employer.employer_nric_nonce,
                'employer_nric_tag':self.employer.employer_nric_tag,
                'employer_fin_num':self.employer.employer_fin_num,
                'employer_fin_nonce':self.employer.employer_fin_nonce,
                'employer_fin_tag':self.employer.employer_fin_tag,
                'employer_passport_num':self.employer.employer_passport_num,
                'employer_passport_nonce':self.employer.employer_passport_nonce,
                'employer_passport_tag':self.employer.employer_passport_tag,
                'employer_passport_date':self.employer.employer_passport_date,
                'employer_marital_status':self.employer.employer_marital_status,
                'employer_marriage_sg_registered':self.employer.employer_marriage_sg_registered,
                'spouse_name':self.employer.spouse_name,
                'spouse_gender':self.employer.spouse_gender,
                'spouse_date_of_birth':self.employer.spouse_date_of_birth,
                'spouse_nationality':self.employer.spouse_nationality,
                'spouse_residential_status':self.employer.spouse_residential_status,
                'spouse_nric_num':self.employer.spouse_nric_num,
                'spouse_nric_nonce':self.employer.spouse_nric_nonce,
                'spouse_nric_tag':self.employer.spouse_nric_tag,
                'spouse_fin_num':self.employer.spouse_fin_num,
                'spouse_fin_nonce':self.employer.spouse_fin_nonce,
                'spouse_fin_tag':self.employer.spouse_fin_tag,
                'spouse_passport_num':self.employer.spouse_passport_num,
                'spouse_passport_nonce':self.employer.spouse_passport_nonce,
                'spouse_passport_tag':self.employer.spouse_passport_tag,
                'spouse_passport_date':self.employer.spouse_passport_date,
                'sponsor_1_relationship':self.employer.rn_sponsor_employer.sponsor_1_relationship,
                'sponsor_1_name':self.employer.rn_sponsor_employer.sponsor_1_name,
                'sponsor_1_gender':self.employer.rn_sponsor_employer.sponsor_1_gender,
                'sponsor_1_date_of_birth':self.employer.rn_sponsor_employer.sponsor_1_date_of_birth,
                'sponsor_1_nric_num':self.employer.rn_sponsor_employer.sponsor_1_nric_num,
                'sponsor_1_nric_nonce':self.employer.rn_sponsor_employer.sponsor_1_nric_nonce,
                'sponsor_1_nric_tag':self.employer.rn_sponsor_employer.sponsor_1_nric_tag,
                'sponsor_1_nationality':self.employer.rn_sponsor_employer.sponsor_1_nationality,
                'sponsor_1_residential_status':self.employer.rn_sponsor_employer.sponsor_1_residential_status,
                'sponsor_1_mobile_number':self.employer.rn_sponsor_employer.sponsor_1_mobile_number,
                'sponsor_1_email':self.employer.rn_sponsor_employer.sponsor_1_email,
                'sponsor_1_address_1':self.employer.rn_sponsor_employer.sponsor_1_address_1,
                'sponsor_1_address_2':self.employer.rn_sponsor_employer.sponsor_1_address_2,
                'sponsor_1_post_code':self.employer.rn_sponsor_employer.sponsor_1_post_code,
                'sponsor_1_marital_status':self.employer.rn_sponsor_employer.sponsor_1_marital_status,
                'sponsor_1_marriage_sg_registered':self.employer.rn_sponsor_employer.sponsor_1_marriage_sg_registered,
                'sponsor_1_spouse_name':self.employer.rn_sponsor_employer.sponsor_1_spouse_name,
                'sponsor_1_spouse_gender':self.employer.rn_sponsor_employer.sponsor_1_spouse_gender,
                'sponsor_1_spouse_date_of_birth':self.employer.rn_sponsor_employer.sponsor_1_spouse_date_of_birth,
                'sponsor_1_spouse_nationality':self.employer.rn_sponsor_employer.sponsor_1_spouse_nationality,
                'sponsor_1_spouse_residential_status':self.employer.rn_sponsor_employer.sponsor_1_spouse_residential_status,
                'sponsor_1_spouse_nric_num':self.employer.rn_sponsor_employer.sponsor_1_spouse_nric_num,
                'sponsor_1_spouse_nric_nonce':self.employer.rn_sponsor_employer.sponsor_1_spouse_nric_nonce,
                'sponsor_1_spouse_nric_tag':self.employer.rn_sponsor_employer.sponsor_1_spouse_nric_tag,
                'sponsor_1_spouse_fin_num':self.employer.rn_sponsor_employer.sponsor_1_spouse_fin_num,
                'sponsor_1_spouse_fin_nonce':self.employer.rn_sponsor_employer.sponsor_1_spouse_fin_nonce,
                'sponsor_1_spouse_fin_tag':self.employer.rn_sponsor_employer.sponsor_1_spouse_fin_tag,
                'sponsor_1_spouse_passport_num':self.employer.rn_sponsor_employer.sponsor_1_spouse_passport_num,
                'sponsor_1_spouse_passport_nonce':self.employer.rn_sponsor_employer.sponsor_1_spouse_passport_nonce,
                'sponsor_1_spouse_passport_tag':self.employer.rn_sponsor_employer.sponsor_1_spouse_passport_tag,
                'sponsor_1_spouse_passport_date':self.employer.rn_sponsor_employer.sponsor_1_spouse_passport_date,
                'sponsor_2_required':self.employer.rn_sponsor_employer.sponsor_2_required,
                'sponsor_2_relationship':self.employer.rn_sponsor_employer.sponsor_2_relationship,
                'sponsor_2_name':self.employer.rn_sponsor_employer.sponsor_2_name,
                'sponsor_2_gender':self.employer.rn_sponsor_employer.sponsor_2_gender,
                'sponsor_2_date_of_birth':self.employer.rn_sponsor_employer.sponsor_2_date_of_birth,
                'sponsor_2_nric_num':self.employer.rn_sponsor_employer.sponsor_2_nric_num,
                'sponsor_2_nric_nonce':self.employer.rn_sponsor_employer.sponsor_2_nric_nonce,
                'sponsor_2_nric_tag':self.employer.rn_sponsor_employer.sponsor_2_nric_tag,
                'sponsor_2_nationality':self.employer.rn_sponsor_employer.sponsor_2_nationality,
                'sponsor_2_residential_status':self.employer.rn_sponsor_employer.sponsor_2_residential_status,
                'sponsor_2_mobile_number':self.employer.rn_sponsor_employer.sponsor_2_mobile_number,
                'sponsor_2_email':self.employer.rn_sponsor_employer.sponsor_2_email,
                'sponsor_2_address_1':self.employer.rn_sponsor_employer.sponsor_2_address_1,
                'sponsor_2_address_2':self.employer.rn_sponsor_employer.sponsor_2_address_2,
                'sponsor_2_post_code':self.employer.rn_sponsor_employer.sponsor_2_post_code,
                'sponsor_2_marital_status':self.employer.rn_sponsor_employer.sponsor_2_marital_status,
                'sponsor_2_marriage_sg_registered':self.employer.rn_sponsor_employer.sponsor_2_marriage_sg_registered,
                'sponsor_2_spouse_name':self.employer.rn_sponsor_employer.sponsor_2_spouse_name,
                'sponsor_2_spouse_gender':self.employer.rn_sponsor_employer.sponsor_2_spouse_gender,
                'sponsor_2_spouse_date_of_birth':self.employer.rn_sponsor_employer.sponsor_2_spouse_date_of_birth,
                'sponsor_2_spouse_nationality':self.employer.rn_sponsor_employer.sponsor_2_spouse_nationality,
                'sponsor_2_spouse_residential_status':self.employer.rn_sponsor_employer.sponsor_2_spouse_residential_status,
                'sponsor_2_spouse_nric_num':self.employer.rn_sponsor_employer.sponsor_2_spouse_nric_num,
                'sponsor_2_spouse_nric_nonce':self.employer.rn_sponsor_employer.sponsor_2_spouse_nric_nonce,
                'sponsor_2_spouse_nric_tag':self.employer.rn_sponsor_employer.sponsor_2_spouse_nric_tag,
                'sponsor_2_spouse_fin_num':self.employer.rn_sponsor_employer.sponsor_2_spouse_fin_num,
                'sponsor_2_spouse_fin_nonce':self.employer.rn_sponsor_employer.sponsor_2_spouse_fin_nonce,
                'sponsor_2_spouse_fin_tag':self.employer.rn_sponsor_employer.sponsor_2_spouse_fin_tag,
                'sponsor_2_spouse_passport_num':self.employer.rn_sponsor_employer.sponsor_2_spouse_passport_num,
                'sponsor_2_spouse_passport_nonce':self.employer.rn_sponsor_employer.sponsor_2_spouse_passport_nonce,
                'sponsor_2_spouse_passport_tag':self.employer.rn_sponsor_employer.sponsor_2_spouse_passport_tag,
                'sponsor_2_spouse_passport_date':self.employer.rn_sponsor_employer.sponsor_2_spouse_passport_date,
                'joint_applicant_relationship':self.employer.rn_ja_employer.joint_applicant_relationship,
                'joint_applicant_name':self.employer.rn_ja_employer.joint_applicant_name,
                'joint_applicant_gender':self.employer.rn_ja_employer.joint_applicant_gender,
                'joint_applicant_date_of_birth':self.employer.rn_ja_employer.joint_applicant_date_of_birth,
                'joint_applicant_nric_num':self.employer.rn_ja_employer.joint_applicant_nric_num,
                'joint_applicant_nric_nonce':self.employer.rn_ja_employer.joint_applicant_nric_nonce,
                'joint_applicant_nric_tag':self.employer.rn_ja_employer.joint_applicant_nric_tag,
                'joint_applicant_nationality':self.employer.rn_ja_employer.joint_applicant_nationality,
                'joint_applicant_residential_status':self.employer.rn_ja_employer.joint_applicant_residential_status,
                'joint_applicant_address_1':self.employer.rn_ja_employer.joint_applicant_address_1,
                'joint_applicant_address_2':self.employer.rn_ja_employer.joint_applicant_address_2,
                'joint_applicant_post_code':self.employer.rn_ja_employer.joint_applicant_post_code,
                'joint_applicant_marital_status':self.employer.rn_ja_employer.joint_applicant_marital_status,
                'joint_applicant_marriage_sg_registered':self.employer.rn_ja_employer.joint_applicant_marriage_sg_registered,
                'joint_applicant_spouse_name':self.employer.rn_ja_employer.joint_applicant_spouse_name,
                'joint_applicant_spouse_gender':self.employer.rn_ja_employer.joint_applicant_spouse_gender,
                'joint_applicant_spouse_date_of_birth':self.employer.rn_ja_employer.joint_applicant_spouse_date_of_birth,
                'joint_applicant_spouse_nationality':self.employer.rn_ja_employer.joint_applicant_spouse_nationality,
                'joint_applicant_spouse_residential_status':self.employer.rn_ja_employer.joint_applicant_spouse_residential_status,
                'joint_applicant_spouse_nric_num':self.employer.rn_ja_employer.joint_applicant_spouse_nric_num,
                'joint_applicant_spouse_nric_nonce':self.employer.rn_ja_employer.joint_applicant_spouse_nric_nonce,
                'joint_applicant_spouse_nric_tag':self.employer.rn_ja_employer.joint_applicant_spouse_nric_tag,
                'joint_applicant_spouse_fin_num':self.employer.rn_ja_employer.joint_applicant_spouse_fin_num,
                'joint_applicant_spouse_fin_nonce':self.employer.rn_ja_employer.joint_applicant_spouse_fin_nonce,
                'joint_applicant_spouse_fin_tag':self.employer.rn_ja_employer.joint_applicant_spouse_fin_tag,
                'joint_applicant_spouse_passport_num':self.employer.rn_ja_employer.joint_applicant_spouse_passport_num,
                'joint_applicant_spouse_passport_nonce':self.employer.rn_ja_employer.joint_applicant_spouse_passport_nonce,
                'joint_applicant_spouse_passport_tag':self.employer.rn_ja_employer.joint_applicant_spouse_passport_tag,
                'joint_applicant_spouse_passport_date':self.employer.rn_ja_employer.joint_applicant_spouse_passport_date,
                'worked_in_sg':self.employer.rn_income_employer.worked_in_sg,
                'monthly_income':self.employer.rn_income_employer.monthly_income,
                'version':self.version,
                'case_ref_no':self.case_ref_no,
                'agreement_date':self.agreement_date,
                'fdw_salary':self.fdw_salary,
                'fdw_loan':self.fdw_loan,
                'fdw_off_days':self.fdw_off_days,
                'fdw_off_day_of_week':self.fdw_off_day_of_week,
                'is_new_case':self.rn_servicefeeschedule_ed.is_new_case,
                'fdw_replaced_name':self.rn_servicefeeschedule_ed.fdw_replaced_name,
                'fdw_replaced_passport_num':self.rn_servicefeeschedule_ed.fdw_replaced_passport_num,
                'fdw_replaced_passport_nonce':self.rn_servicefeeschedule_ed.fdw_replaced_passport_nonce,
                'fdw_replaced_passport_tag':self.rn_servicefeeschedule_ed.fdw_replaced_passport_tag,
                'b4_loan_transferred':self.rn_servicefeeschedule_ed.b4_loan_transferred,
                'b1_service_fee':self.rn_servicefeeschedule_ed.b1_service_fee,
                'b2a_work_permit_application_collection':self.rn_servicefeeschedule_ed.b2a_work_permit_application_collection,
                'b2b_medical_examination_fee':self.rn_servicefeeschedule_ed.b2b_medical_examination_fee,
                'b2c_security_bond_accident_insurance':self.rn_servicefeeschedule_ed.b2c_security_bond_accident_insurance,
                'b2d_indemnity_policy_reimbursement':self.rn_servicefeeschedule_ed.b2d_indemnity_policy_reimbursement,
                'b2e_home_service':self.rn_servicefeeschedule_ed.b2e_home_service,
                'b2f_sip':self.rn_servicefeeschedule_ed.b2f_sip,
                'b2g1_other_services_description':self.rn_servicefeeschedule_ed.b2g1_other_services_description,
                'b2g1_other_services_fee':self.rn_servicefeeschedule_ed.b2g1_other_services_fee,
                'b2g2_other_services_description':self.rn_servicefeeschedule_ed.b2g2_other_services_description,
                'b2g2_other_services_fee':self.rn_servicefeeschedule_ed.b2g2_other_services_fee,
                'b2g3_other_services_description':self.rn_servicefeeschedule_ed.b2g3_other_services_description,
                'b2g3_other_services_fee':self.rn_servicefeeschedule_ed.b2g3_other_services_fee,
                'b2h_replacement_months':self.rn_servicefeeschedule_ed.b2h_replacement_months,
                'b2h_replacement_cost':self.rn_servicefeeschedule_ed.b2h_replacement_cost,
                'b2i_work_permit_renewal':self.rn_servicefeeschedule_ed.b2i_work_permit_renewal,
                'b3_agency_fee':self.rn_servicefeeschedule_ed.b3_agency_fee,
                'ca_deposit_amount':self.rn_servicefeeschedule_ed.ca_deposit_amount,
                'ca_deposit_date':self.rn_servicefeeschedule_ed.ca_deposit_date,
                'c1_3_handover_days':self.rn_serviceagreement_ed.c1_3_handover_days,
                'c3_2_no_replacement_criteria_1':self.rn_serviceagreement_ed.c3_2_no_replacement_criteria_1,
                'c3_2_no_replacement_criteria_2':self.rn_serviceagreement_ed.c3_2_no_replacement_criteria_2,
                'c3_2_no_replacement_criteria_3':self.rn_serviceagreement_ed.c3_2_no_replacement_criteria_3,
                'c3_4_no_replacement_refund':self.rn_serviceagreement_ed.c3_4_no_replacement_refund,
                'c4_1_number_of_replacements':self.rn_serviceagreement_ed.c4_1_number_of_replacements,
                'c4_1_replacement_period':self.rn_serviceagreement_ed.c4_1_replacement_period,
                'c4_1_replacement_after_min_working_days':self.rn_serviceagreement_ed.c4_1_replacement_after_min_working_days,
                'c4_1_5_replacement_deadline':self.rn_serviceagreement_ed.c4_1_5_replacement_deadline,
                'c5_1_1_deployment_deadline':self.rn_serviceagreement_ed.c5_1_1_deployment_deadline,
                'c5_1_1_failed_deployment_refund':self.rn_serviceagreement_ed.c5_1_1_failed_deployment_refund,
                'c5_1_2_refund_within_days':self.rn_serviceagreement_ed.c5_1_2_refund_within_days,
                'c5_1_2_before_fdw_arrives_charge':self.rn_serviceagreement_ed.c5_1_2_before_fdw_arrives_charge,
                'c5_1_2_after_fdw_arrives_charge':self.rn_serviceagreement_ed.c5_1_2_after_fdw_arrives_charge,
                'c5_2_2_can_transfer_refund_within':self.rn_serviceagreement_ed.c5_2_2_can_transfer_refund_within,
                'c5_3_2_cannot_transfer_refund_within':self.rn_serviceagreement_ed.c5_3_2_cannot_transfer_refund_within,
                'c6_4_per_day_food_accommodation_cost':self.rn_serviceagreement_ed.c6_4_per_day_food_accommodation_cost,
                'c6_6_per_session_counselling_cost':self.rn_serviceagreement_ed.c6_6_per_session_counselling_cost,
                'c9_1_independent_mediator_1':self.rn_serviceagreement_ed.c9_1_independent_mediator_1,
                'c9_2_independent_mediator_2':self.rn_serviceagreement_ed.c9_2_independent_mediator_2,
                'c13_termination_notice':self.rn_serviceagreement_ed.c13_termination_notice,
                'c3_5_fdw_sleeping_arrangement':self.rn_serviceagreement_ed.c3_5_fdw_sleeping_arrangement,
                'c4_1_termination_notice':self.rn_serviceagreement_ed.c4_1_termination_notice,
                'residential_dwelling_type':self.rn_safetyagreement_ed.residential_dwelling_type,
                'fdw_clean_window_exterior':self.rn_safetyagreement_ed.fdw_clean_window_exterior,
                'window_exterior_location':self.rn_safetyagreement_ed.window_exterior_location,
                'grilles_installed_require_cleaning':self.rn_safetyagreement_ed.grilles_installed_require_cleaning,
                'adult_supervision':self.rn_safetyagreement_ed.adult_supervision,
                'verifiy_employer_understands_window_cleaning':self.rn_safetyagreement_ed.verifiy_employer_understands_window_cleaning,
                'employer_signature':self.rn_signatures_ed.employer_signature,
                'fdw_signature':self.rn_signatures_ed.fdw_signature,
                'agency_staff_signature':self.rn_signatures_ed.agency_staff_signature,
                'ipa_approval_date':self.rn_casestatus_ed.ipa_approval_date,
                'arrival_date':self.rn_casestatus_ed.arrival_date,
                'shn_end_date':self.rn_casestatus_ed.shn_end_date,
                'thumb_print_date':self.rn_casestatus_ed.thumb_print_date,
                'fdw_work_commencement_date':self.rn_casestatus_ed.fdw_work_commencement_date,
                #START OF TODO
                'f01_service_fee_schedule':None,
                'f03_service_agreement':None,
                'f04_employment_contract':None,
                'f05_repayment_schedule':None,
                'f06_rest_day_agreement':None,
                'f08_handover_checklist':None,
                'f09_transfer_consent':None,
                'f10_work_pass_authorisation':None,
                'f14_safety_agreement':None,
                #END OF TODO
                'job_order_pdf':self.rn_docupload_ed.job_order_pdf,
                'ipa_pdf':self.rn_docupload_ed.ipa_pdf,
                'e_issuance_pdf':self.rn_docupload_ed.e_issuance_pdf,
                'medical_report_pdf':self.rn_docupload_ed.medical_report_pdf
            }
        )

class DocServiceFeeSchedule(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_servicefeeschedule_ed'
    )
    is_new_case = models.BooleanField(
        verbose_name=_("Type of case (Form A / Form B)"),
        choices=TrueFalseChoices(
            _('New case (Form A)'),
            _('Replacement case (Form B)'),
        ),
        default=True,
    )
    fdw_replaced_name = models.CharField(
        verbose_name=_("Name of FDW Replaced"),
        max_length=50,
        blank=True,
        null=True,
    )
    fdw_replaced_passport_num = models.BinaryField(
        verbose_name=_('Passport No. of FDW Replaced'),
        editable=True,
        blank=True,
        null=True,
    )
    fdw_replaced_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    fdw_replaced_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    b4_loan_transferred = CustomMoneyDecimalField(
        verbose_name=_("4. Loan Transferred"),
        blank=True,
        null=True,
        help_text=_("Loan amount brought forward from FDW replaced"),
    )

    b1_service_fee = CustomMoneyDecimalField(
        verbose_name=_("1. Service Fee")
    )
    b2a_work_permit_application_collection = CustomMoneyDecimalField(
        verbose_name=_("2a. Application / Collection of Work Permit")
    )
    b2b_medical_examination_fee = CustomMoneyDecimalField(
        verbose_name=_("2b. Medical Examination Fee")
    )
    b2c_security_bond_accident_insurance = CustomMoneyDecimalField(
        verbose_name=_("2c. Security Bond and Personal Accident Insurance")
    )
    b2d_indemnity_policy_reimbursement = CustomMoneyDecimalField(
        verbose_name=_("2d. Reimbursement of Indemnity Policy")
    )
    b2e_home_service = CustomMoneyDecimalField(
        verbose_name=_("2e. Home Service")
    )
    b2f_sip = CustomMoneyDecimalField(
        verbose_name=_("2f. Settling-In-Programme (SIP)")
    )
    b2g1_other_services_description = models.CharField(
        verbose_name=_("2g. Other services provided (i)"),
        max_length=40,
        blank=True,
        null=True
    )
    b2g1_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (i)"),
        blank=True,
        null=True
    )
    b2g2_other_services_description = models.CharField(
        verbose_name=_("2g. Other services provided (ii)"),
        max_length=40,
        blank=True,
        null=True,
    )
    b2g2_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (ii)"),
        blank=True,
        null=True
    )
    b2g3_other_services_description = models.CharField(
        verbose_name=_("2g. Other services provided (iii)"),
        max_length=40,
        blank=True,
        null=True,
    )
    b2g3_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (iii)"),
        blank=True,
        null=True
    )
    b2h_replacement_months = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("2h. Cost for replacement within __ month(s)"),
        choices=ed_constants.MonthChoices.choices,
        blank=True,
        null=True,
    )
    b2h_replacement_cost = CustomMoneyDecimalField(
        verbose_name=_("2h. Cost for replacement"),
        blank=True,
        null=True
    )
    b2i_work_permit_renewal = CustomMoneyDecimalField(
        verbose_name=_("2i. Renewal of Work Permit"),
        blank=True,
        null=True
    )
    b3_agency_fee = CustomMoneyDecimalField(
        verbose_name=_("3a. Agency fee"),
        help_text=_('Agency fee charged on the FDW by the Agency')
    )
    ca_deposit_amount = CustomMoneyDecimalField(
        verbose_name=_("2c. Deposit - upon confirmation of FDW"),
        help_text=_('Deposit paid by Employer')
    )
    ca_deposit_date = models.DateField(
        verbose_name=_('Deposit Paid Date'),
    )

    def calc_admin_cost(self):
        # Method to calculate total administrative cost
        total = 0
        fields = [
            self.b1_service_fee,
            self.b2a_work_permit_application_collection,
            self.b2b_medical_examination_fee,
            self.b2c_security_bond_accident_insurance,
            self.b2d_indemnity_policy_reimbursement,
            self.b2e_home_service,
            self.b2f_sip,
            self.b2g1_other_services_fee,
            self.b2g2_other_services_fee,
            self.b2g3_other_services_fee,
            self.b2h_replacement_cost,
            self.b2i_work_permit_renewal,
        ]
        for field in fields:
            # Sum this way because some fields may be null
            total += field if field else 0
        return total

    def calc_placement_fee(self):
        # Method to calculate placement fee
        return (
            + self.b3_agency_fee
            + self.employer_doc.fdw_loan
        )

    def calc_total_fee(self):
        # Method to calculate total fee
        return self.calc_admin_cost() + self.calc_placement_fee()

    def calc_bal(self):
        # Method to calculate outstanding balance owed by employer
        balance = (
            self.calc_admin_cost()
            + self.calc_placement_fee()
            - self.ca_deposit_amount
        )
        return balance

    def get_fdw_replaced_passport_full(self):
        return decrypt_string(
            self.fdw_replaced_passport_num,
            settings.ENCRYPTION_KEY,
            self.fdw_replaced_passport_nonce,
            self.fdw_replaced_passport_tag,
        )

class DocServAgmtEmpCtr(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_serviceagreement_ed'
    )

    # Service Agreement
    c1_3_handover_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("1.3 handover FDW to Employer within __ day(s)"),
        choices=ed_constants.DayChoices.choices
    )
    c3_2_no_replacement_criteria_1 = models.CharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (i)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_2 = models.CharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (ii)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_3 = models.CharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (iii)"),
        max_length=100
    )
    c3_4_no_replacement_refund = CustomMoneyDecimalField(
        verbose_name=_("3.4 Refund amount if no replacement pursuant to Clause \
            3.1")
    )
    c4_1_number_of_replacements = models.PositiveSmallIntegerField(
        verbose_name=_("4.1 Number of replacement FDWs that Employer is entitled \
            to"),
        choices=[
            (0, _("0 replacements")),
            (1, _("1 replacement")),
            (2, _("2 replacements")),
            (3, _("3 replacements")),
            (4, _("4 replacements")),
            (5, _("5 replacements")),
            (6, _("6 replacements")),
            (7, _("7 replacements")),
            (8, _("8 replacements")),
            (9, _("9 replacements")),
            (10, _("10 replacements")),
        ]
    )
    c4_1_replacement_period = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("4.1 Replacement FDW period validity (months)"),
        choices=ed_constants.MonthChoices.choices
    )
    c4_1_replacement_after_min_working_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("4.1 Replacement only after FDW has worked for minimum of \
            __ day(s)"),
        choices=ed_constants.DayChoices.choices
    )
    c4_1_5_replacement_deadline = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("4.1.5 Replacement FDW provided within __ month(s) from \
            date FDW returned"),
        choices=ed_constants.MonthChoices.choices
    )
    c5_1_1_deployment_deadline = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.1 Deploy FDW to Employer within __ day(s) of date of \
            Service Agreement"),
        choices=ed_constants.DayChoices.choices
    )
    c5_1_1_failed_deployment_refund = CustomMoneyDecimalField(
        verbose_name=_("5.1.1 Failed FDW deployment refund amount")
    )
    c5_1_2_refund_within_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.2 If Employer terminates Agreement, Employer entitled \
            to Service Fee refund within __ day(s)"),
        choices=ed_constants.DayChoices.choices
    )
    c5_1_2_before_fdw_arrives_charge = CustomMoneyDecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates BEFORE FDW arrives in \
            Singapore")
    )
    c5_1_2_after_fdw_arrives_charge = CustomMoneyDecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates AFTER FDW arrives in \
            Singapore")
    )
    c5_2_2_can_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.2.2 If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=ed_constants.WeekChoices.choices
    )
    c5_3_2_cannot_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.3.2 If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=ed_constants.WeekChoices.choices
    )
    c6_4_per_day_food_accommodation_cost = CustomMoneyDecimalField(
        verbose_name=_("6.4 Food and Accommodation cost per day")
    )
    c6_6_per_session_counselling_cost = CustomMoneyDecimalField(
        verbose_name=_("6.6 Counselling cost per day")
    )
    c9_1_independent_mediator_1 = models.CharField(
        verbose_name=_("9.1 Independent mediator #1"),
        max_length=40,
        blank=True,
        null=True,
    )
    c9_2_independent_mediator_2 = models.CharField(
        verbose_name=_("9.2 Independent mediator #2"),
        max_length=40,
        blank=True,
        null=True,
    )
    c13_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("13. Service Agreement termination notice (days)"),
        choices=ed_constants.DayChoices.choices
    )
    
    # Employment Contract
    c3_5_fdw_sleeping_arrangement = models.CharField(
        verbose_name=_("3.5 FDW sleeping arrangement"),
        max_length=6,
        choices=[
            ("OWN", _("have her own room")),
            ("SHARE", _("sharing room with someone")),
            ("COMMON", _("sleeping in common area")),
        ],
        default='OWN',
    )
    c4_1_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("4.1 Employment Contract termination notice (days)"),
        choices=ed_constants.DayChoices.choices
    )

class DocSafetyAgreement(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_safetyagreement_ed'
    )
    residential_dwelling_type = models.CharField(
        max_length=6,
        choices=[
            ("HDB", _("HDB Apartment")),
            ("CONDO", _("Private Apartment/Condominium")),
            ("LANDED", _("Landed Property")),
        ],
        default='HDB',
    )
    fdw_clean_window_exterior = models.BooleanField(
        verbose_name=_('Does Employer require FDW to clean window exterior?'),
        choices=TrueFalseChoices(
            _('Yes, clean window exterior'),
            _('No, not required'),
        ),
        default=False,
        help_text=_('If yes, must complete field (i).'),
    )
    window_exterior_location = models.CharField(
        verbose_name=_("(i) Location of window exterior"),
        max_length=6,
        choices=[
            ("GROUND", _("On the ground floor")),
            ("COMMON", _("Facing common corridor")),
            ("OTHER", _("Other")),
        ],
        blank=True,
        null=True,
        help_text=_("If 'Other' is selected, must complete field (ii)."),
    )
    grilles_installed_require_cleaning = models.BooleanField(
        verbose_name=_('(ii) Grilles installed on windows required to be cleaned by FDW?'),
        choices=TrueFalseChoices(
            _('Yes, grilles installed require cleaning'),
            _('No, not required'),
        ),
        blank=True,
        null=True,
        help_text=_('If yes, must complete field (iii).'),
    )
    adult_supervision = models.BooleanField(
        verbose_name=_('(iii) Adult supervision when cleaning window exterior?'),
        choices=TrueFalseChoices(
            _('Yes, adult supervision'),
            _('No supervision'),
        ),
        blank=True,
        null=True,
    )
    verifiy_employer_understands_window_cleaning = models.PositiveSmallIntegerField(
        verbose_name=_("Verifiy employer understands window cleaning conditions"),
        choices=[
            (1, _("FDW not required to clean window exterior")),
            (2, _("FDW to clean only window exterior on ground floor")),
            (3, _("FDW to clean only window exterior along common corridor")),
            (4, _("Ensure grilles are locked and only cleaned under adult supervision")),
        ],
        default='not_required_to_clean_window_exterior',
    )

    def save(self):
        if self.fdw_clean_window_exterior==False:
            self.window_exterior_location = None
            self.grilles_installed_require_cleaning = None
            self.adult_supervision = None

        elif not self.window_exterior_location=='OTHER':
            self.grilles_installed_require_cleaning = None
            self.adult_supervision = None

        elif not self.grilles_installed_require_cleaning:
            self.adult_supervision = None

        return super().save()

class DocUpload(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_docupload_ed'
    )
    job_order_pdf = models.FileField(
        verbose_name=_('Job Order (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    ipa_pdf = models.FileField(
        verbose_name=_('IPA (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    e_issuance_pdf = models.FileField(
        verbose_name=_('E-Issuance Document (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    medical_report_pdf = models.FileField(
        verbose_name=_('Medical Report (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

class CaseSignature(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_signatures_ed'
    )

    # Mandatory signatures
    employer_signature_1 = models.TextField(
        # For docs excluding handover checklist
        verbose_name=_('Employer Signature'),
        blank=True,
        null=True
    )
    employer_signature_2 = models.TextField(
        # For handover checklist
        verbose_name=_('Employer Signature'),
        blank=True,
        null=True
    )
    fdw_signature = models.TextField(
        verbose_name=_('FDW Signature'),
        blank=True,
        null=True
    )
    agency_staff_signature = models.TextField(
        verbose_name=_('Agency Staff Member Signature'),
        blank=True,
        null=True
    )

    # Optional signatures
    employer_spouse_signature = models.TextField(
        verbose_name=_('Employer Spouse Signature'),
        blank=True,
        null=True
    )
    sponsor_1_signature = models.TextField(
        verbose_name=_('Sponsor 1 Signature'),
        blank=True,
        null=True
    )
    sponsor_2_signature = models.TextField(
        verbose_name=_('Sponsor 2 Signature'),
        blank=True,
        null=True
    )
    joint_applicant_signature = models.TextField(
        verbose_name=_('Joint Applicant Signature'),
        blank=True,
        null=True
    )

    # Signature URL slugs
    sigslug_employer_1 = models.SlugField(
        max_length=255,
        unique=True,
        default=None,
        blank=True,
        null=True
    )

    sigslug_employer_spouse = models.SlugField(
        max_length=255,
        unique=True,
        default=None,
        blank=True,
        null=True
    )

    sigslug_sponsor_1 = models.SlugField(
        max_length=255,
        unique=True,
        default=None,
        blank=True,
        null=True
    )

    sigslug_sponsor_2 = models.SlugField(
        max_length=255,
        unique=True,
        default=None,
        blank=True,
        null=True
    )

    sigslug_joint_applicant = models.SlugField(
        max_length=255,
        unique=True,
        default=None,
        blank=True,
        null=True
    )

    def generate_sigslug(self, stakeholder):
        if stakeholder == 'employer_1':
            self.sigslug_employer_1 = secrets.token_urlsafe(128)
        elif stakeholder == 'employer_spouse':
            self.sigslug_employer_spouse = secrets.token_urlsafe(128)
        elif stakeholder == 'sponsor_1':
            self.sigslug_sponsor_1 = secrets.token_urlsafe(128)
        elif stakeholder == 'sponsor_2':
            self.sigslug_sponsor_2 = secrets.token_urlsafe(128)
        elif stakeholder == 'joint_applicant':
            self.sigslug_joint_applicant = secrets.token_urlsafe(128)
        super().save()

    def revoke_sigslug(self, stakeholder):
        if stakeholder == 'employer_1':
            self.sigslug_employer_1 = None
        elif stakeholder == 'employer_spouse':
            self.sigslug_employer_spouse = None
        elif stakeholder == 'sponsor_1':
            self.sigslug_sponsor_1 = None
        elif stakeholder == 'sponsor_2':
            self.sigslug_sponsor_2 = None
        elif stakeholder == 'joint_applicant':
            self.sigslug_joint_applicant = None
        super().save()

    def get_sigurl(self, stakeholder):
        current_site = Site.objects.get_current()
        sigurl_challenge_route_dict = {
            # Stakeholder: View Url Name
            'employer_1': 'challenge_employer1_route',
            'employer_spouse': 'challenge_employer1_route',
            'sponsor_1': 'challenge_employer1_route',
            'sponsor_2': 'challenge_employer1_route',
            'joint_applicant': 'challenge_employer1_route'
        }

        kwargs = None
        if stakeholder == 'employer_1' and self.sigslug_employer_1:
            kwargs={
                'slug': self.sigslug_employer_1
            }
        elif stakeholder == 'employer_spouse' and self.sigslug_employer_spouse:
            kwargs={
                'slug': self.sigslug_employer_spouse
            }
        elif stakeholder == 'sponsor_1' and self.sigslug_sponsor_1:
            kwargs={
                'slug': self.sigslug_sponsor_1
            }
        elif stakeholder == 'sponsor_2' and self.sigslug_sponsor_2:
            kwargs={
                'slug': self.sigslug_sponsor_2
            }
        elif stakeholder == 'joint_applicant' and self.sigslug_joint_applicant:
            kwargs={
                'slug': self.sigslug_joint_applicant
            }
        
        if kwargs:
            relative_url = reverse(
                sigurl_challenge_route_dict[stakeholder],
                kwargs=kwargs
            )
            return current_site.domain + relative_url

    # Verification Tokens
    token_employer_1 = models.BinaryField(
        blank=True,
        null=True,
    )

class CaseStatus(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_casestatus_ed'
    )
    ipa_approval_date = models.DateField(
        verbose_name=_('In Principle Approval (IPA) Date'),
        blank=True,
        null=True
    )
    arrival_date = models.DateField(
        verbose_name=_('FDW Arrival Date'),
        blank=True,
        null=True
    )
    shn_end_date = models.DateField(
        verbose_name=_('SHN End Date'),
        blank=True,
        null=True
    )
    thumb_print_date = models.DateField(
        verbose_name=_('FDW Thumb Print Date'),
        blank=True,
        null=True
    )
    fdw_work_commencement_date = models.DateField(
        verbose_name=_('Deployment Date'),
        blank=True,
        null=True
    )

class ArchivedAgencyDetails(models.Model):
    name = models.CharField(
        verbose_name=_('Agency Name'),
        max_length=255
    )

    license_no = models.CharField(
        verbose_name=_('Agency License Number'),
        max_length=255
    )

    address_line_1 = models.CharField(
        verbose_name=_('Agency Registered Business Address Line 1'),
        max_length=255
    )

    address_line_2 = models.CharField(
        verbose_name=_('Agency Registered Business Address Line 2'),
        max_length=255
    )

    postal_code = models.CharField(
        verbose_name=_('Agency Registered Business Postal Code'),
        max_length=20
    )

    agency_employee_name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=False
    )

    agency_employee_ea_personnel_number = models.CharField(
        verbose_name=_('EA personnel number'),
        max_length=50,
        default='NA',
        blank=True,
        help_text=_('Optional for non-personnel')
    )

class ArchivedMaid(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=False
    )

    nationality = models.CharField(
        verbose_name=_('Nationality'),
        max_length=255,
        blank=False
    )

    passport_number = models.BinaryField(
        editable=True,
        blank=True
    )

    passport_number_nonce = models.BinaryField(
        editable=True,
        blank=True
    )

    passport_number_tag = models.BinaryField(
        editable=True,
        blank=True
    )

    work_permit_number = models.CharField(
        verbose_name=_('Work Permit Number'),
        max_length=255,
        blank=False
    )

class ArchivedDoc(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    applicant_type = models.CharField(
        verbose_name=_("Type of Applicant"),
        max_length=6,
        choices=ed_constants.EmployerTypeOfApplicantChoices.choices,
        default=ed_constants.EmployerTypeOfApplicantChoices.SINGLE,
    )

    # Agency Informtaion
    agency_name = models.CharField(
        verbose_name=_('Agency Name'),
        max_length=255
    )

    agency_license_no = models.CharField(
        verbose_name=_('Agency License Number'),
        max_length=255
    )

    agency_address_line_1 = models.CharField(
        verbose_name=_('Agency Registered Business Address Line 1'),
        max_length=255
    )

    agency_address_line_2 = models.CharField(
        verbose_name=_('Agency Registered Business Address Line 2'),
        max_length=255
    )

    agency_postal_code = models.CharField(
        verbose_name=_('Agency Registered Business Postal Code'),
        max_length=20
    )

    agency_employee_name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=False
    )

    agency_employee_ea_personnel_number = models.CharField(
        verbose_name=_('EA personnel number'),
        max_length=50,
        default='NA',
        blank=True,
        help_text=_('Optional for non-personnel')
    )
    
    # Maid Information
    maid_name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=False
    )

    maid_nationality = models.CharField(
        verbose_name=_('Nationality'),
        max_length=255,
        blank=False
    )

    maid_passport_number = models.BinaryField(
        editable=True,
        blank=True
    )

    maid_passport_number_nonce = models.BinaryField(
        editable=True,
        blank=True
    )

    maid_passport_number_tag = models.BinaryField(
        editable=True,
        blank=True
    )

    maid_work_permit_number = models.CharField(
        verbose_name=_('Work Permit Number'),
        max_length=255,
        blank=False
    )

    # Employer Information
    employer_name = models.CharField(
        verbose_name=_('Employer Name'),
        max_length=40,
    )
    
    employer_gender = models.CharField(
        verbose_name=_("Employer gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
    )
    
    employer_mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$', # Singapore mobile numbers
                message=_('Please enter a valid mobile number')
            )
        ],
    )
    
    employer_home_number = models.CharField(
        verbose_name=_('Home Tel Number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[6][0-9]{7}$', # Singapore landline numbers
                message=_('Please enter a valid home telephone number')
            )
        ],
    )
    
    employer_email = models.EmailField(
        verbose_name=_('Email Address')
    )

    employer_address_1 = models.CharField(
        verbose_name=_('Address Line 1'),
        max_length=100,
    )
    
    employer_address_2 = models.CharField(
        verbose_name=_('Address Line 2'),
        max_length=50,
        blank=True,
        null=True,
    )
    
    employer_post_code = models.CharField(
        verbose_name=_('Postal Code'),
        max_length=25,
    )

    employer_date_of_birth = models.DateField(
        verbose_name=_('Employer date of birth'),
    )

    employer_nationality = models.CharField(
        verbose_name=_("Employer nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )

    employer_residential_status = models.CharField(
        verbose_name=_("Employer residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
    )

    employer_nric_num = models.BinaryField(
        verbose_name=_('Employer NRIC'),
        editable=True,
    )

    employer_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True
    )

    employer_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True
    )

    employer_fin_num = models.BinaryField(
        verbose_name=_('Employer FIN'),
        editable=True,
        blank=True,
        null=True,
    )
    
    employer_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    employer_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    employer_passport_num = models.BinaryField(
        verbose_name=_('Employer passport'),
        editable=True,
        blank=True,
        null=True,
    )
    
    employer_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    employer_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    
    employer_passport_date = models.DateField(
        verbose_name=_('Employer passport expiry date'),
        blank=True,
        null=True,
    )
    
    employer_marital_status = models.CharField(
        verbose_name=_("Employer marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
        blank=True,
        null=True,
    )
    
    employer_marriage_sg_registered = models.BooleanField(
        verbose_name=_('Employer marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Employer's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )

    def get_employer_nric_full(self):
        return decrypt_string(
            self.employer_nric_num,
            settings.ENCRYPTION_KEY,
            self.employer_nric_nonce,
            self.employer_nric_tag,
        )
    
    def get_employer_nric_partial(self):
        plaintext = self.get_employer_nric_full()
        return 'x'*5 + plaintext[-4:] if plaintext else ''

    def get_employer_fin_full(self):
        return decrypt_string(
            self.employer_fin_num,
            settings.ENCRYPTION_KEY,
            self.employer_fin_nonce,
            self.employer_fin_tag,
        )

    def get_employer_passport(self):
        return decrypt_string(
            self.employer_passport_num,
            settings.ENCRYPTION_KEY,
            self.employer_passport_nonce,
            self.employer_passport_tag,
        )

    def get_spouse_nric_full(self):
        return decrypt_string(
            self.spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.spouse_nric_nonce,
            self.spouse_nric_tag,
        )
    
    def get_spouse_fin(self):
        return decrypt_string(
            self.spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.spouse_fin_nonce,
            self.spouse_fin_tag,
        )

    def get_spouse_passport(self):
        return decrypt_string(
            self.spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.spouse_passport_nonce,
            self.spouse_passport_tag,
        )

    def mobile_partial_sg(self):
        return '+65 ' + self.employer_mobile_number[:4] + ' ' + 'x'*4

    def get_email_partial(self):
        return self.employer_email[:3] + '_'*8 + self.employer_email[-3:]

    ## Employer Spouse
    spouse_name = models.CharField(
        verbose_name=_("Spouse's Name"),
        max_length=40,
        blank=True,
        null=True,
        default=None,
    )
    spouse_gender = models.CharField(
        verbose_name=_("Spouse's gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    spouse_date_of_birth = models.DateField(
        verbose_name=_("Spouse's date of birth"),
        blank=True,
        null=True,
    )
    spouse_nationality = models.CharField(
        verbose_name=_("Spouse's nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    spouse_residential_status = models.CharField(
        verbose_name=_("Spouse's residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    spouse_nric_num = models.BinaryField(
        verbose_name=_("Spouse's NRIC"),
        editable=True,
        blank=True,
        null=True,
    )
    spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    spouse_fin_num = models.BinaryField(
        verbose_name=_("Spouse's FIN"),
        editable=True,
        blank=True,
        null=True,
    )
    spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    spouse_passport_num = models.BinaryField(
        verbose_name=_("Spouse's Passport No"),
        editable=True,
        blank=True,
        null=True,
    )
    spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    spouse_passport_date = models.DateField(
        verbose_name=_("Spouse's Passport Expiry Date"),
        blank=True,
        null=True,
    )

    def get_employer_spouse_nric_full(self):
        return decrypt_string(
            self.spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.spouse_nric_nonce,
            self.spouse_nric_tag,
        )

    def get_employer_spouse_fin_full(self):
        return decrypt_string(
            self.spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.spouse_fin_nonce,
            self.spouse_fin_tag,
        )

    def get_employer_spouse_passport_full(self):
        return decrypt_string(
            self.spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.spouse_passport_nonce,
            self.spouse_passport_tag,
        )

    ## Sponsors
    # Sponsor 1 details
    sponsor_1_relationship = models.CharField(
        verbose_name=_("Sponsor 1 relationship with Employer"),
        max_length=30,
        choices=ed_constants.RelationshipChoices.choices,
        default=ed_constants.RelationshipChoices.DAUGHTER,
    )
    sponsor_1_name = models.CharField(
        verbose_name=_('Sponsor 1 Name'),
        max_length=40,
    )
    sponsor_1_gender = models.CharField(
        verbose_name=_("Sponsor 1 gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
    )
    sponsor_1_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 1 date of birth'),
    )
    sponsor_1_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 1 NRIC'),
        editable=True,
    )
    sponsor_1_nric_nonce = models.BinaryField(
        editable=True,
    )
    sponsor_1_nric_tag = models.BinaryField(
        editable=True,
    )
    sponsor_1_nationality = models.CharField(
        verbose_name=_("Sponsor 1 nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
    )
    sponsor_1_residential_status = models.CharField(
        verbose_name=_("Sponsor 1 residential status"),
        max_length=2,
        choices=ed_constants.ResidentialStatusPartialChoices.choices,
        default=ed_constants.ResidentialStatusPartialChoices.SC,
    )
    sponsor_1_mobile_number = models.CharField(
        verbose_name=_('Sponsor 1 mobile number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$', # Singapore mobile numbers
                message=_('Please enter a valid contact number')
            )
        ],
    )
    sponsor_1_email = models.EmailField(
        verbose_name=_('Sponsor 1 email address'),
    )
    sponsor_1_address_1 = models.CharField(
        verbose_name=_('Sponsor 1 Address Line 1'),
        max_length=100,
    )
    sponsor_1_address_2 = models.CharField(
        verbose_name=_('Sponsor 1 Address Line 2'),
        max_length=50,
        blank=True,
        null=True,
    )
    sponsor_1_post_code = models.CharField(
        verbose_name=_('Sponsor 1 Postal Code'),
        max_length=25,
    )
    sponsor_1_marital_status = models.CharField(
        verbose_name=_("Sponsor 1 marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
    )

    # Sponsor 1 spouse details
    sponsor_1_marriage_sg_registered = models.BooleanField(
        verbose_name=_('Sponsor 1 marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Sponsor 1's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )
    sponsor_1_spouse_name = models.CharField(
        verbose_name=_('Sponsor 1 spouse name'),
        max_length=40,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_gender = models.CharField(
        verbose_name=_("Sponsor 1 spouse gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 1 spouse date of birth'),
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nationality = models.CharField(
        verbose_name=_("Sponsor 1 spouse nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_residential_status = models.CharField(
        verbose_name=_("Sponsor 1 spouse residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 1 spouse NRIC'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_fin_num = models.BinaryField(
        verbose_name=_('Sponsor 1 spouse FIN'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_num = models.BinaryField(
        verbose_name=_('Sponsor 1 spouse passport'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_1_spouse_passport_date = models.DateField(
        verbose_name=_('Sponsor 1 spouse passport expiry date'),
        blank=True,
        null=True,
    )

    # Sponsor required?
    sponsor_2_required = models.BooleanField(
        verbose_name=_('Do you need to add Sponsor 2?'),
        default=False,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
    )

    # Sponsor 2 details
    sponsor_2_relationship = models.CharField(
        verbose_name=_("Sponsor 2 relationship with Employer"),
        max_length=30,
        choices=ed_constants.RelationshipChoices.choices,
        default=ed_constants.RelationshipChoices.DAUGHTER,
        blank=True,
        null=True,
    )
    sponsor_2_name = models.CharField(
        verbose_name=_('Sponsor 2 Name'),
        max_length=40,
        blank=True,
        null=True,
    )
    sponsor_2_gender = models.CharField(
        verbose_name=_("Sponsor 2 gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    sponsor_2_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 2 date of birth'),
        blank=True,
        null=True,
    )
    sponsor_2_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 2 NRIC'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_nationality = models.CharField(
        verbose_name=_("Sponsor 2 nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    sponsor_2_residential_status = models.CharField(
        verbose_name=_("Sponsor 2 residential status"),
        max_length=2,
        choices=ed_constants.ResidentialStatusPartialChoices.choices,
        default=ed_constants.ResidentialStatusPartialChoices.SC,
        blank=True,
        null=True,
    )
    sponsor_2_mobile_number = models.CharField(
        verbose_name=_('Sponsor 2 mobile number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$', # Singapore mobile numbers
                message=_('Please enter a valid contact number')
            )
        ],
        blank=True,
        null=True,
    )
    sponsor_2_email = models.EmailField(
        verbose_name=_('Sponsor 2 email address'),
        blank=True,
        null=True,
    )
    sponsor_2_address_1 = models.CharField(
        verbose_name=_('Sponsor 2 Address Line 1'),
        max_length=100,
        blank=True,
        null=True,
    )
    sponsor_2_address_2 = models.CharField(
        verbose_name=_('Sponsor 2 Address Line 2'),
        max_length=50,
        blank=True,
        null=True,
    )
    sponsor_2_post_code = models.CharField(
        verbose_name=_('Sponsor 2 Postal Code'),
        max_length=25,
        blank=True,
        null=True,
    )
    sponsor_2_marital_status = models.CharField(
        verbose_name=_("Sponsor 2 marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
        blank=True,
        null=True,
    )
    sponsor_2_marriage_sg_registered = models.BooleanField(
        verbose_name=_('Sponsor 2 marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Sponsor 2's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )

    # Sponsor 2 spouse details
    sponsor_2_spouse_name = models.CharField(
        verbose_name=_('Sponsor 2 spouse name'),
        max_length=40,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_gender = models.CharField(
        verbose_name=_("Sponsor 2 spouse gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 2 spouse date of birth'),
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nationality = models.CharField(
        verbose_name=_("Sponsor 2 spouse nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_residential_status = models.CharField(
        verbose_name=_("Sponsor 2 spouse residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 2 spouse NRIC'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_fin_num = models.BinaryField(
        verbose_name=_('Sponsor 2 spouse FIN'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_num = models.BinaryField(
        verbose_name=_('Sponsor 2 spouse passport'),
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    sponsor_2_spouse_passport_date = models.DateField(
        verbose_name=_('Sponsor 2 spouse passport expiry date'),
        blank=True,
        null=True,
    )

    def get_sponsor_1_nric_full(self):
        return decrypt_string(
            self.sponsor_1_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_nric_nonce,
            self.sponsor_1_nric_tag,
        )

    def get_sponsor_1_spouse_nric_full(self):
        return decrypt_string(
            self.sponsor_1_spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_spouse_nric_nonce,
            self.sponsor_1_spouse_nric_tag,
        )

    def get_sponsor_1_spouse_fin_full(self):
        return decrypt_string(
            self.sponsor_1_spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_spouse_fin_nonce,
            self.sponsor_1_spouse_fin_tag,
        )

    def get_sponsor_1_spouse_passport_full(self):
        return decrypt_string(
            self.sponsor_1_spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_spouse_passport_nonce,
            self.sponsor_1_spouse_passport_tag,
        )
    
    def get_sponsor_2_nric_full(self):
        return decrypt_string(
            self.sponsor_2_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_nric_nonce,
            self.sponsor_2_nric_tag,
        )

    def get_sponsor_2_spouse_nric_full(self):
        return decrypt_string(
            self.sponsor_2_spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_spouse_nric_nonce,
            self.sponsor_2_spouse_nric_tag,
        )

    def get_sponsor_2_spouse_fin_full(self):
        return decrypt_string(
            self.sponsor_2_spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_spouse_fin_nonce,
            self.sponsor_2_spouse_fin_tag,
        )

    def get_sponsor_2_spouse_passport_full(self):
        return decrypt_string(
            self.sponsor_2_spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_2_spouse_passport_nonce,
            self.sponsor_2_spouse_passport_tag,
        )

    # Joint Applicants
    joint_applicant_relationship = models.CharField(
        verbose_name=_("Joint applicant's relationship with Employer"),
        max_length=30,
        choices=ed_constants.RelationshipChoices.choices,
        default=ed_constants.RelationshipChoices.DAUGHTER,
    )
    joint_applicant_name = models.CharField(
        verbose_name=_("Joint applicant's Name"),
        max_length=40,
    )
    joint_applicant_gender = models.CharField(
        verbose_name=_("Joint applicant's gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
    )
    joint_applicant_date_of_birth = models.DateField(
        verbose_name=_("Joint applicant's date of birth"),
    )
    joint_applicant_nric_num = models.BinaryField(
        verbose_name=_('Joint applicant NRIC'),
        editable=True,
    )
    joint_applicant_nric_nonce = models.BinaryField(
        editable=True,
    )
    joint_applicant_nric_tag = models.BinaryField(
        editable=True,
    )
    joint_applicant_nationality = models.CharField(
        verbose_name=_("Joint applicant's nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
    )
    joint_applicant_residential_status = models.CharField(
        verbose_name=_("Joint applicant's residential status"),
        max_length=2,
        choices=ed_constants.ResidentialStatusPartialChoices.choices,
        default=ed_constants.ResidentialStatusPartialChoices.SC,
    )
    joint_applicant_address_1 = models.CharField(
        verbose_name=_("Joint applicant's Address Line 1"),
        max_length=100,
    )
    joint_applicant_address_2 = models.CharField(
        verbose_name=_("Joint applicant's Address Line 2"),
        max_length=50,
        blank=True,
        null=True,
    )
    joint_applicant_post_code = models.CharField(
        verbose_name=_("Joint applicant's Postal Code"),
        max_length=25,
    )
    joint_applicant_marital_status = models.CharField(
        verbose_name=_("Joint applicant's marital status"),
        max_length=10,
        choices=ed_constants.MaritalStatusChoices.choices,
        default=ed_constants.MaritalStatusChoices.SINGLE,
    )
    joint_applicant_marriage_sg_registered = models.BooleanField(
        verbose_name=_("Joint applicant's marriage registered in SG?"),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Joint applicant's marriage registered in Singapore?
        '''),
        blank=True,
        null=True,
    )

    # Joint applicant's spouse details
    joint_applicant_spouse_name = models.CharField(
        verbose_name=_("Joint applicant's spouse name"),
        max_length=40,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_gender = models.CharField(
        verbose_name=_("Joint applicant's spouse gender"),
        max_length=1,
        choices=ed_constants.GenderChoices.choices,
        default=ed_constants.GenderChoices.F,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_date_of_birth = models.DateField(
        verbose_name=_("Joint applicant's spouse date of birth"),
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nationality = models.CharField(
        verbose_name=_("Joint applicant's spouse nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_residential_status = models.CharField(
        verbose_name=_("Joint applicant's spouse residential status"),
        max_length=5,
        choices=ed_constants.ResidentialStatusFullChoices.choices,
        default=ed_constants.ResidentialStatusFullChoices.SC,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nric_num = models.BinaryField(
        verbose_name=_("Joint applicant's spouse NRIC"),
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_fin_num = models.BinaryField(
        verbose_name=_("Joint applicant's spouse FIN"),
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_fin_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_fin_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_num = models.BinaryField(
        verbose_name=_("Joint applicant's spouse passport"),
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_spouse_passport_date = models.DateField(
        verbose_name=_("Joint applicant's spouse passport expiry date"),
        blank=True,
        null=True,
    )

    def get_joint_applicant_nric_full(self):
        return decrypt_string(
            self.joint_applicant_nric_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_nric_nonce,
            self.joint_applicant_nric_tag,
        )
    
    def get_joint_applicant_spouse_nric_full(self):
        return decrypt_string(
            self.joint_applicant_spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_spouse_nric_nonce,
            self.joint_applicant_spouse_nric_tag,
        )

    def get_joint_applicant_spouse_fin_full(self):
        return decrypt_string(
            self.joint_applicant_spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_spouse_fin_nonce,
            self.joint_applicant_spouse_fin_tag,
        )

    def get_joint_applicant_spouse_passport_full(self):
        return decrypt_string(
            self.joint_applicant_spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_spouse_passport_nonce,
            self.joint_applicant_spouse_passport_tag,
        )

    # Income Details
    worked_in_sg = models.BooleanField(
        verbose_name=_('Have you worked in Singapore for the last 2 Years?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
    )
    monthly_income = models.PositiveSmallIntegerField(
        verbose_name=_("Monthly Income"),
        choices=ed_constants.IncomeChoices.choices,
        default=ed_constants.IncomeChoices.INCOME_3,
    )

    # Doc Base
    version = models.PositiveSmallIntegerField(
        editable=False,
        default=0,
    )
    case_ref_no = models.CharField(
        verbose_name=_("Case Reference Number"),
        max_length=20,
        unique=True,
    )
    agreement_date = models.DateField(
        verbose_name=_("Contract Date"),
    )
    fdw = models.OneToOneField(
        ArchivedMaid,
        verbose_name=_("Name of FDW"),
        on_delete=models.RESTRICT,
    )
    fdw_salary = CustomMoneyDecimalField(
        verbose_name=_("FDW Basic Salary"),
        help_text=_("FDW monthly salary per contract")
    )
    fdw_loan = CustomMoneyDecimalField(
        verbose_name=_("FDW Loan Amount"),
        help_text=_("FDW loan amount per contract")
    )
    fdw_off_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("FDW No. of off-days per month"),
        choices=ed_constants.DayChoices.choices[0:5],
        default=4,
        help_text=_("FDW off-days a month per contract"),
    )
    fdw_off_day_of_week = models.PositiveSmallIntegerField(
        verbose_name=_("FDW Off Day Day of Week"),
        choices=ed_constants.DayOfWeekChoices.choices,
        default=ed_constants.DayOfWeekChoices.SUN
    )

    def get_version(self):
        return str(self.version).zfill(4)

    # Service Fee Schedule
    is_new_case = models.BooleanField(
        verbose_name=_("Type of case (Form A / Form B)"),
        choices=TrueFalseChoices(
            _('New case (Form A)'),
            _('Replacement case (Form B)'),
        ),
        default=True,
    )
    fdw_replaced_name = models.CharField(
        verbose_name=_("Name of FDW Replaced"),
        max_length=50,
        blank=True,
        null=True,
    )
    fdw_replaced_passport_num = models.BinaryField(
        verbose_name=_('Passport No. of FDW Replaced'),
        editable=True,
        blank=True,
        null=True,
    )
    fdw_replaced_passport_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    fdw_replaced_passport_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    b4_loan_transferred = CustomMoneyDecimalField(
        verbose_name=_("4. Loan Transferred"),
        blank=True,
        null=True,
        help_text=_("Loan amount brought forward from FDW replaced")
    )

    b1_service_fee = CustomMoneyDecimalField(
        verbose_name=_("1. Service Fee")
    )
    b2a_work_permit_application_collection = CustomMoneyDecimalField(
        verbose_name=_("2a. Application / Collection of Work Permit")
    )
    b2b_medical_examination_fee = CustomMoneyDecimalField(
        verbose_name=_("2b. Medical Examination Fee")
    )
    b2c_security_bond_accident_insurance = CustomMoneyDecimalField(
        verbose_name=_("2c. Security Bond and Personal Accident Insurance")
    )
    b2d_indemnity_policy_reimbursement = CustomMoneyDecimalField(
        verbose_name=_("2d. Reimbursement of Indemnity Policy")
    )
    b2e_home_service = CustomMoneyDecimalField(
        verbose_name=_("2e. Home Service")
    )
    b2f_sip = CustomMoneyDecimalField(
        verbose_name=_("2f. Settling-In-Programme (SIP)")
    )
    b2g1_other_services_description = models.CharField(
        verbose_name=_("2g. Other services provided (i)"),
        max_length=40,
        blank=True,
        null=True
    )
    b2g1_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (i)"),
        blank=True,
        null=True
    )
    b2g2_other_services_description = models.CharField(
        verbose_name=_("2g. Other services provided (ii)"),
        max_length=40,
        blank=True,
        null=True,
    )
    b2g2_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (ii)"),
        blank=True,
        null=True
    )
    b2g3_other_services_description = models.CharField(
        verbose_name=_("2g. Other services provided (iii)"),
        max_length=40,
        blank=True,
        null=True,
    )
    b2g3_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (iii)"),
        blank=True,
        null=True
    )
    b2h_replacement_months = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("2h. Cost for replacement within __ month(s)"),
        choices=ed_constants.MonthChoices.choices,
        blank=True,
        null=True,
    )
    b2h_replacement_cost = CustomMoneyDecimalField(
        verbose_name=_("2h. Cost for replacement"),
        blank=True,
        null=True
    )
    b2i_work_permit_renewal = CustomMoneyDecimalField(
        verbose_name=_("2i. Renewal of Work Permit"),
        blank=True,
        null=True
    )
    b3_agency_fee = CustomMoneyDecimalField(
        verbose_name=_("3a. Agency fee"),
        help_text=_('Agency fee charged on the FDW by the Agency')
    )
    ca_deposit_amount = CustomMoneyDecimalField(
        verbose_name=_("2c. Deposit - upon confirmation of FDW"),
        help_text=_('Deposit paid by Employer')
    )
    ca_deposit_date = models.DateField(
        verbose_name=_('Deposit Paid Date'),
    )

    def calc_admin_cost(self):
        # Method to calculate total administrative cost
        total = 0
        fields = [
            self.b1_service_fee,
            self.b2a_work_permit_application_collection,
            self.b2b_medical_examination_fee,
            self.b2c_security_bond_accident_insurance,
            self.b2d_indemnity_policy_reimbursement,
            self.b2e_home_service,
            self.b2f_counselling,
            self.b2g_sip,
            self.b2h_food_lodging,
            self.b2i1_other_services_fee,
            self.b2i2_other_services_fee,
            self.b2i3_other_services_fee,
            self.b2j_replacement_cost,
            self.b2k_work_permit_renewal,
        ]
        for field in fields:
            # Sum this way because some fields may be null
            total += field if field else 0
        return total

    def calc_placement_fee(self):
        # Method to calculate placement fee
        return (
            + self.b3_agency_fee
            + self.b3_fdw_loan
        )

    def calc_total_fee(self):
        # Method to calculate total fee
        return self.calc_admin_cost() + self.calc_placement_fee()

    def calc_bal(self):
        # Method to calculate outstanding balance owed by employer
        balance = (
            self.calc_admin_cost()
            + self.calc_placement_fee()
            - self.ca_deposit_amount
        )

        return balance

    def get_fdw_replaced_passport_full(self):
        return decrypt_string(
            self.fdw_replaced_passport_num,
            settings.ENCRYPTION_KEY,
            self.fdw_replaced_passport_nonce,
            self.fdw_replaced_passport_tag,
        )

    # Service Agreement
    c1_3_handover_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("1.3 handover FDW to Employer within __ day(s)"),
        choices=ed_constants.DayChoices.choices
    )
    c3_2_no_replacement_criteria_1 = models.CharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (i)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_2 = models.CharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (ii)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_3 = models.CharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (iii)"),
        max_length=100
    )
    c3_4_no_replacement_refund = CustomMoneyDecimalField(
        verbose_name=_("3.4 Refund amount if no replacement pursuant to Clause \
            3.1")
    )
    c4_1_number_of_replacements = models.PositiveSmallIntegerField(
        verbose_name=_("4.1 Number of replacement FDWs that Employer is entitled \
            to"),
        choices=[
            (0, _("0 replacements")),
            (1, _("1 replacement")),
            (2, _("2 replacements")),
            (3, _("3 replacements")),
            (4, _("4 replacements")),
            (5, _("5 replacements")),
            (6, _("6 replacements")),
            (7, _("7 replacements")),
            (8, _("8 replacements")),
            (9, _("9 replacements")),
            (10, _("10 replacements")),
        ]
    )
    c4_1_replacement_period = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("4.1 Replacement FDW period validity (months)"),
        choices=ed_constants.MonthChoices.choices
    )
    c4_1_replacement_after_min_working_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("4.1 Replacement only after FDW has worked for minimum of \
            __ day(s)"),
        choices=ed_constants.DayChoices.choices
    )
    c4_1_5_replacement_deadline = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("4.1.5 Replacement FDW provided within __ month(s) from \
            date FDW returned"),
        choices=ed_constants.MonthChoices.choices
    )
    c5_1_1_deployment_deadline = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.1 Deploy FDW to Employer within __ day(s) of date of \
            Service Agreement"),
        choices=ed_constants.DayChoices.choices
    )
    c5_1_1_failed_deployment_refund = CustomMoneyDecimalField(
        verbose_name=_("5.1.1 Failed FDW deployment refund amount")
    )
    c5_1_2_refund_within_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.2 If Employer terminates Agreement, Employer entitled \
            to Service Fee refund within __ day(s)"),
        choices=ed_constants.DayChoices.choices
    )
    c5_1_2_before_fdw_arrives_charge = CustomMoneyDecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates BEFORE FDW arrives in \
            Singapore")
    )
    c5_1_2_after_fdw_arrives_charge = CustomMoneyDecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates AFTER FDW arrives in \
            Singapore")
    )
    c5_2_2_can_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.2.2 If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=ed_constants.WeekChoices.choices
    )
    c5_3_2_cannot_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.3.2 If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=ed_constants.WeekChoices.choices
    )
    c6_4_per_day_food_accommodation_cost = CustomMoneyDecimalField(
        verbose_name=_("6.4 Food and Accommodation cost per day")
    )
    c6_6_per_session_counselling_cost = CustomMoneyDecimalField(
        verbose_name=_("6.6 Counselling cost per day")
    )
    c9_1_independent_mediator_1 = models.CharField(
        verbose_name=_("9.1 Independent mediator #1"),
        max_length=40,
        blank=True,
        null=True,
    )
    c9_2_independent_mediator_2 = models.CharField(
        verbose_name=_("9.2 Independent mediator #2"),
        max_length=40,
        blank=True,
        null=True,
    )
    c13_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("13. Service Agreement termination notice (days)"),
        choices=ed_constants.DayChoices.choices
    )
    
    # Employment Contract
    c3_5_fdw_sleeping_arrangement = models.CharField(
        verbose_name=_("3.5 FDW sleeping arrangement"),
        max_length=6,
        choices=[
            ("OWN", _("have her own room")),
            ("SHARE", _("sharing room with someone")),
            ("COMMON", _("sleeping in common area")),
        ],
        default='OWN',
    )
    c4_1_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("4.1 Employment Contract termination notice (days)"),
        choices=ed_constants.DayChoices.choices
    )

    # Safety Agreement
    residential_dwelling_type = models.CharField(
        max_length=6,
        choices=[
            ("HDB", _("HDB Apartment")),
            ("CONDO", _("Private Apartment/Condominium")),
            ("LANDED", _("Landed Property")),
        ],
        blank=True,
        null=True,
        default='HDB',
    )
    fdw_clean_window_exterior = models.BooleanField(
        verbose_name=_('Does Employer require FDW to clean window exterior?'),
        choices=TrueFalseChoices(
            _('Yes, clean window exterior'),
            _('No, not required'),
        ),
        blank=True,
        null=True,
        default=False,
        help_text=_('If yes, must complete field (i).'),
    )
    window_exterior_location = models.CharField(
        verbose_name=_("(i) Location of window exterior"),
        max_length=6,
        choices=[
            ("GROUND", _("On the ground floor")),
            ("COMMON", _("Facing common corridor")),
            ("OTHER", _("Other")),
        ],
        blank=True,
        null=True,
        help_text=_("If 'Other' is selected, must complete field (ii)."),
    )
    grilles_installed_require_cleaning = models.BooleanField(
        verbose_name=_('(ii) Grilles installed on windows required to be cleaned by FDW?'),
        choices=TrueFalseChoices(
            _('Yes, grilles installed require cleaning'),
            _('No, not required'),
        ),
        blank=True,
        null=True,
        help_text=_('If yes, must complete field (iii).'),
    )
    adult_supervision = models.BooleanField(
        verbose_name=_('(iii) Adult supervision when cleaning window exterior?'),
        choices=TrueFalseChoices(
            _('Yes, adult supervision'),
            _('No supervision'),
        ),
        blank=True,
        null=True,
    )
    verifiy_employer_understands_window_cleaning = models.PositiveSmallIntegerField(
        verbose_name=_("Verifiy employer understands window cleaning conditions"),
        choices=[
            (1, _("FDW not required to clean window exterior")),
            (2, _("FDW to clean only window exterior on ground floor")),
            (3, _("FDW to clean only window exterior along common corridor")),
            (4, _("Ensure grilles are locked and only cleaned under adult supervision")),
        ],
        blank=True,
        null=True,
        default='not_required_to_clean_window_exterior',
    )

    # Mandatory signatures
    employer_signature = models.TextField(
        verbose_name=_('Employer Signature'),
        blank=True,
        null=True
    )
    fdw_signature = models.TextField(
        verbose_name=_('FDW Signature'),
        blank=True,
        null=True
    )
    agency_staff_signature = models.TextField(
        verbose_name=_('Agency Staff Member Signature'),
        blank=True,
        null=True
    )

    # Status dates
    ipa_approval_date = models.DateField(
        verbose_name=_('In Principle Approval (IPA) Date'),
    )
    arrival_date = models.DateField(
        verbose_name=_('FDW Arrival Date'),
    )
    shn_end_date = models.DateField(
        verbose_name=_('SHN End Date'),
    )
    thumb_print_date = models.DateField(
        verbose_name=_('FDW Thumb Print Date'),
    )
    fdw_work_commencement_date = models.DateField(
        verbose_name=_('Deployment Date'),
    )

    # System generated PDF files
    f01_service_fee_schedule = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f03_service_agreement = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f04_employment_contract = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f05_repayment_schedule = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f06_rest_day_agreement = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f08_handover_checklist = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f09_transfer_consent = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f10_work_pass_authorisation = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    # f11_security_bond = models.FileField(
    #     upload_to=generate_archive_path,
    #     storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    # )
    # f12_fdw_work_permit = models.FileField(
    #     upload_to=generate_archive_path,
    #     storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    # )
    f13_income_tax_declaration = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
    )
    f14_safety_agreement = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )

    # Uploaded PDF files
    job_order_pdf = models.FileField(
        verbose_name=_('Upload Job Order (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    ipa_pdf = models.FileField(
        verbose_name=_('Upload IPA (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    e_issuance_pdf = models.FileField(
        verbose_name=_('Upload E-Issuance Document (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    medical_report_pdf = models.FileField(
        verbose_name=_('Upload Medical Report (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

# class ArchivedEmployerHousehold(models.Model):
#     employer = models.ForeignKey(
#         ArchivedDoc,
#         verbose_name=_("Name of Employer"),
#         on_delete=models.CASCADE,
#         related_name="rn_archivedhousehold_employer",
#     )
#     # Household Details
#     household_name = models.CharField(
#         verbose_name=_("Household member's name"),
#         max_length=40,
#     )
#     household_id_type = models.CharField(
#         verbose_name=_("Household member ID type"),
#         max_length=8,
#         choices=ed_constants.HouseholdIdTypeChoices.choices,
#         # default=ed_constants.HouseholdIdTypeChoices.NRIC,
#     )
#     household_id_num = models.BinaryField(
#         verbose_name=_("Household member's ID number"),
#         editable=True,
#     )
#     household_date_of_birth = models.DateField(
#         verbose_name=_("Household member's date of birth"),
#     )
#     household_relationship = models.CharField(
#         verbose_name=_("Household member's relationship with Employer"),
#         max_length=30,
#         choices=ed_constants.RelationshipChoices.choices,
#         # default=ed_constants.RelationshipChoices.DAUGHTER,
#     )

#     def get_household_id_full(self):
#         return decrypt_string(
#             self.household_id_num,
#             settings.ENCRYPTION_KEY,
#             self.household_id_nonce,
#             self.household_id_tag,
#         )
