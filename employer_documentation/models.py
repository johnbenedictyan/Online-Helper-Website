# Imports from python
import os
import uuid

# Imports from django
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.core.validators import (
    FileExtensionValidator,
    MinValueValidator,
    MaxValueValidator,
)

# Imports from other apps
from onlinemaid.constants import TrueFalseChoices
from onlinemaid.helper_functions import decrypt_string
from onlinemaid.storage_backends import EmployerDocumentationStorage
from agency.models import AgencyEmployee
from maid.models import Maid
from maid.constants import FullNationsChoices

# Same app
from .constants import (
    IncomeChoices,
    RelationshipChoices,
    GenderChoices,
    ResidentialStatusFullChoices,
    ResidentialStatusPartialChoices,
    MaritalStatusChoices,
    HouseholdIdTypeChoices,
)

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
    # 'employerdoc_pk:name_of_file.pdf'
    filename_split = filename.split(':')
    employerdoc_pk = filename_split[0]
    relative_path = 'archive/' + employerdoc_pk
    # return the whole path to the file
    return os.path.join(relative_path, filename_split[-1])

def get_mobile_format_sg(mobile):
    return '+65 ' + mobile[:4] + ' ' + mobile[4:]


# Start of Models

# Employer e-Documentation Models
class Employer(models.Model):
    APPLICANT_TYPE_CHOICES = [
        ('SINGLE', _("Employer Only")),
        ('SPOUSE', _("Employer with Spouse")),
        ('SPONS1', _("Employer with 1 Sponsor")),
        ('SPONS2', _("Employer with 2 Sponsors")),
        ('JNT_AP', _("Employer with Joint Applicant")),
    ]
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    applicant_type = models.CharField(
        verbose_name=_("Type of Applicant"),
        max_length=6,
        choices=APPLICANT_TYPE_CHOICES,
        default=APPLICANT_TYPE_CHOICES[0][0],
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
        choices=GenderChoices.choices,
        default=GenderChoices.F,
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
    employer_email = models.EmailField(verbose_name=_('Email Address'))
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
        choices=ResidentialStatusFullChoices.choices,
        default=ResidentialStatusFullChoices.SC,
    )
    employer_nric_num = models.BinaryField(
        verbose_name=_('Employer NRIC'),
        editable=True,
    )
    employer_nric_nonce = models.BinaryField(editable=True)
    employer_nric_tag = models.BinaryField(editable=True)
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
        choices=MaritalStatusChoices.choices,
        default=MaritalStatusChoices.SINGLE,
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

    def mobile_format_sg(self):
        return '+65 ' + self.employer_mobile_number[:4] + ' ' + self.employer_mobile_number[4:]

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
        choices=GenderChoices.choices,
        default=GenderChoices.F,
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
        choices=ResidentialStatusFullChoices.choices,
        default=ResidentialStatusFullChoices.SC,
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

    # Income Details
    monthly_income = models.PositiveSmallIntegerField(
        verbose_name=_("Employer monthly income / combined income with spouse"),
        choices=IncomeChoices.choices,
        default=IncomeChoices.INCOME_3,
        blank=True,
        null=True,
    )

    # Household Details
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
    household_name = models.CharField(
        verbose_name=_("Household member's name"),
        max_length=40,
        blank=True,
        null=True,
    )
    household_date_of_birth = models.DateField(
        verbose_name=_("Household member's date of birth"),
        blank=True,
        null=True,
    )
    household_id_type = models.CharField(
        verbose_name=_("Household member ID type"),
        max_length=8,
        choices=HouseholdIdTypeChoices.choices,
        # default=HouseholdIdTypeChoices.NRIC,
        blank=True,
        null=True,
    )
    household_id_num = models.CharField(
        verbose_name=_("Household member's ID number"),
        max_length=20,
        blank=True,
        null=True,
    )
    household_relationship = models.CharField(
        verbose_name=_("Household member's relationship with Employer"),
        max_length=30,
        choices=RelationshipChoices.choices,
        # default=RelationshipChoices.DAUGHTER,
        blank=True,
        null=True,
    )

## Sponsors
class EmployerSponsor(models.Model):
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='rn_sponsor_employer'
    )
    
    # Sponsor 1 details
    sponsor_1_relationship = models.CharField(
        verbose_name=_("Sponsor 1 relationship with Employer"),
        max_length=30,
        choices=RelationshipChoices.choices,
        default=RelationshipChoices.DAUGHTER,
    )
    sponsor_1_worked_in_sg = models.BooleanField(
        verbose_name=_('Sponsor 1 worked in SG for last 2 years?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
    )
    sponsor_1_name = models.CharField(
        verbose_name=_('Sponsor 1 Name'),
        max_length=40,
    )
    sponsor_1_gender = models.CharField(
        verbose_name=_("Sponsor 1 gender"),
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.F,
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
        choices=ResidentialStatusPartialChoices.choices,
        default=ResidentialStatusPartialChoices.SC,
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
        choices=MaritalStatusChoices.choices,
        default=MaritalStatusChoices.SINGLE,
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
        choices=GenderChoices.choices,
        default=GenderChoices.F,
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
        choices=ResidentialStatusFullChoices.choices,
        default=ResidentialStatusFullChoices.SC,
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

    # Sponsor 2 details
    sponsor_2_relationship = models.CharField(
        verbose_name=_("Sponsor 2 relationship with Employer"),
        max_length=30,
        choices=RelationshipChoices.choices,
        default=RelationshipChoices.DAUGHTER,
        blank=True,
        null=True,
    )
    sponsor_2_worked_in_sg = models.BooleanField(
        verbose_name=_('Sponsor 1 worked in SG for last 2 years?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
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
        choices=GenderChoices.choices,
        default=GenderChoices.F,
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
        choices=ResidentialStatusPartialChoices.choices,
        default=ResidentialStatusPartialChoices.SC,
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
        choices=MaritalStatusChoices.choices,
        default=MaritalStatusChoices.SINGLE,
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
        choices=GenderChoices.choices,
        default=GenderChoices.F,
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
        choices=ResidentialStatusFullChoices.choices,
        default=ResidentialStatusFullChoices.SC,
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

    # Income Details
    monthly_income = models.PositiveSmallIntegerField(
        verbose_name=_("Sponsor's monthly income or sponsors' combined monthly income"),
        choices=IncomeChoices.choices,
        default=IncomeChoices.INCOME_3,
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

    def get_sponsor_1_mobile(self):
        return get_mobile_format_sg(self.sponsor_1_mobile_number)

    def get_sponsor_2_mobile(self):
        return get_mobile_format_sg(self.sponsor_2_mobile_number) if self.sponsor_2_mobile_number else None

## Joint Applicants
class EmployerJointApplicant(models.Model):
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='rn_ja_employer'
    )
    monthly_income = models.PositiveSmallIntegerField(
        verbose_name=_("Combined monthly income of Employer and Joint applicant"),
        choices=IncomeChoices.choices,
        default=IncomeChoices.INCOME_3,
        blank=True,
        null=True,
    )
    joint_applicant_worked_in_sg = models.BooleanField(
        verbose_name=_('Employer and Joint applicant worked in SG for last 2 years?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Have both Employer and Joint applicant worked in Singapore for the last 2 years?
        '''),
        blank=True,
        null=True,
    )

    joint_applicant_relationship = models.CharField(
        verbose_name=_("Joint applicant's relationship with Employer"),
        max_length=30,
        choices=RelationshipChoices.choices,
        default=RelationshipChoices.DAUGHTER,
        blank=True,
        null=True,
    )
    joint_applicant_name = models.CharField(
        verbose_name=_("Joint applicant's Name"),
        max_length=40,
        blank=True,
        null=True,
    )
    joint_applicant_gender = models.CharField(
        verbose_name=_("Joint applicant's gender"),
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.F,
        blank=True,
        null=True,
    )
    joint_applicant_date_of_birth = models.DateField(
        verbose_name=_("Joint applicant's date of birth"),
        blank=True,
        null=True,
    )
    joint_applicant_nric_num = models.BinaryField(
        verbose_name=_('Joint applicant NRIC'),
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_nric_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_nric_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True,
    )
    joint_applicant_nationality = models.CharField(
        verbose_name=_("Joint applicant's nationality/citizenship"),
        max_length=3,
        choices=FullNationsChoices.choices,
        default=FullNationsChoices.SINGAPORE,
        blank=True,
        null=True,
    )
    joint_applicant_residential_status = models.CharField(
        verbose_name=_("Joint applicant's residential status"),
        max_length=2,
        choices=ResidentialStatusPartialChoices.choices,
        default=ResidentialStatusPartialChoices.SC,
        blank=True,
        null=True,
    )
    joint_applicant_address_1 = models.CharField(
        verbose_name=_("Joint applicant's Address Line 1"),
        max_length=100,
        blank=True,
        null=True,
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
        blank=True,
        null=True,
    )
    joint_applicant_marital_status = models.CharField(
        verbose_name=_("Joint applicant's marital status"),
        max_length=10,
        choices=MaritalStatusChoices.choices,
        default=MaritalStatusChoices.SINGLE,
        blank=True,
        null=True,
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
        choices=GenderChoices.choices,
        default=GenderChoices.F,
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
        choices=ResidentialStatusFullChoices.choices,
        default=ResidentialStatusFullChoices.SC,
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

class EmployerDoc(models.Model):
    DAY_CHOICES = [
        (0, _("0 days")),
        (1, _("1 day")),
        (2, _("2 days")),
        (3, _("3 days")),
        (4, _("4 days")),
        (5, _("5 days")),
        (6, _("6 days")),
        (7, _("7 days")),
        (8, _("8 days")),
        (9, _("9 days")),
        (10, _("10 days")),
        (11, _("11 days")),
        (12, _("12 days")),
        (13, _("13 days")),
        (14, _("14 days")),
        (15, _("15 days")),
        (16, _("16 days")),
        (17, _("17 days")),
        (18, _("18 days")),
        (19, _("19 days")),
        (20, _("20 days")),
        (21, _("21 days")),
        (22, _("22 days")),
        (23, _("23 days")),
        (24, _("24 days")),
        (25, _("25 days")),
        (26, _("26 days")),
        (27, _("27 days")),
        (28, _("28 days")),
    ]

    WEEK_CHOICES = [
        (0, _("0 weeks")),
        (1, _("1 week")),
        (2, _("2 weeks")),
        (3, _("3 weeks")),
        (4, _("4 weeks")),
    ]

    MONTH_CHOICES = [
        (0, _("0 months")),
        (1, _("1 month")),
        (2, _("2 months")),
        (3, _("3 months")),
        (4, _("4 months")),
        (5, _("5 months")),
        (6, _("6 months")),
        (7, _("7 months")),
        (8, _("8 months")),
        (9, _("9 months")),
        (10, _("10 months")),
        (11, _("11 months")),
        (12, _("12 months")),
        (13, _("13 months")),
        (14, _("14 months")),
        (15, _("15 months")),
        (16, _("16 months")),
        (17, _("17 months")),
        (18, _("18 months")),
        (19, _("19 months")),
        (20, _("20 months")),
        (21, _("21 months")),
        (22, _("22 months")),
        (23, _("23 months")),
        (24, _("24 months")),
    ]
    SCHEME_CHOICES = [
        ('SINGL', _("Employer Only")),
        ('SPOUS', _("Employer and Spouse")),
        ('JOINT', _("Joint Income")),
        ('SPONS', _("Sponsorship")),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    version = models.PositiveSmallIntegerField(
        editable=False,
        default=0,
    )
    case_ref_no = models.CharField(
        verbose_name=_("Case Reference Number"),
        max_length=20,
        unique=True
    )
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name='rn_ed_employer'
    )
    fdw = models.ForeignKey(
        Maid,
        verbose_name=_("Foreign Domestic Worker (FDW)"),
        on_delete=models.RESTRICT
    )
    agreement_date = models.DateField(
        verbose_name=_('Agreement Date for Signed Documents'),
    )
    application_scheme = models.CharField(
        verbose_name=_("Application scheme"),
        max_length=5,
        choices=SCHEME_CHOICES,
        default=SCHEME_CHOICES[0][0],
    )

    # Service Fee Schedule
    b1_service_fee = models.DecimalField(
        verbose_name=_("1. Service Fee"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2a_work_permit_application_collection = models.DecimalField(
        verbose_name=_("2a. Application / Collection of Work Permit"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2b_medical_examination_fee = models.DecimalField(
        verbose_name=_("2b. Medical Examination Fee"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2c_security_bond_accident_insurance = models.DecimalField(
        verbose_name=_("2c. Security Bond and Personal Accident Insurance"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2d_indemnity_policy_reimbursement = models.DecimalField(
        verbose_name=_("2d. Reimbursement of Indemnity Policy"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2e_home_service = models.DecimalField(
        verbose_name=_("2e. Home Service"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2f_counselling = models.DecimalField(
        verbose_name=_("2f. Each Counselling Session"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2g_sip = models.DecimalField(
        verbose_name=_("2g. Settling-In-Programme (SIP)"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2h_replacement_months = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("2h. Cost for replacement within __ month(s)"),
        choices=MONTH_CHOICES
    )
    b2h_replacement_cost = models.DecimalField(
        verbose_name=_("2h. Cost for replacement"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2i_work_permit_renewal = models.DecimalField(
        verbose_name=_("2i. Renewal of Work Permit"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    b2j1_other_services_description = models.CharField(
        verbose_name=_("2j. Other services provided (i)"),
        max_length=40,
        blank=True,
        null=True
    )
    b2j1_other_services_fee = models.DecimalField(
        verbose_name=_("2j. Other services fee (i)"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        blank=True,
        null=True,
    )
    b2j2_other_services_description = models.CharField(
        verbose_name=_("2j. Other services provided (ii)"),
        max_length=40,
        blank=True,
        null=True,
    )
    b2j2_other_services_fee = models.DecimalField(
        verbose_name=_("2j. Other services fee (ii)"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        blank=True,
        null=True,
    )
    b2j3_other_services_description = models.CharField(
        verbose_name=_("2j. Other services provided (iii)"),
        max_length=40,
        blank=True,
        null=True,
    )
    b2j3_other_services_fee = models.DecimalField(
        verbose_name=_("2j. Other services fee (iii)"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        blank=True,
        null=True,
    )
    b3_agency_fee = models.DecimalField(
        verbose_name=_("3a. Agency fee"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        help_text=_('Agency fee charged on the FDW by the Agency'),
    )
    b3_fdw_loan = models.DecimalField(
        verbose_name=_("3b. FDW personal loan"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        help_text=_('Personal loan incurred by FDW in overseas'),
    )
    ca_deposit = models.DecimalField(
        verbose_name=_("2c. Deposit - upon confirmation of FDW"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        help_text=_('Deposit paid by Employer'),
    )

    # If FDW is replacement, then additional fields
    fdw_is_replacement = models.BooleanField(
        verbose_name=_("Is this FDW a replacement? (Form A / Form B)"),
        choices=TrueFalseChoices(
            _('Yes, replacement (Form B)'),
            _('No, not replacement (Form A)'),
        ),
        default=False,
    )
    fdw_replaced = models.ForeignKey(
        Maid,
        verbose_name=_("FDW Replaced* (required if FDW is replacement)"),
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name='rn_ed_fdwreplaced',
    )
    b4_loan_transferred = models.DecimalField(
        verbose_name=_("4. Loan Transferred* (required if FDW is replacement)"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        blank=True,
        null=True,
    )

    # Service Agreement
    c1_3_handover_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("1.3 handover FDW to Employer within __ day(s)"),
        choices=DAY_CHOICES
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
    c3_4_no_replacement_refund = models.DecimalField(
        verbose_name=_("3.4 Refund amount if no replacement pursuant to Clause \
            3.1"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
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
        choices=MONTH_CHOICES
    )
    c4_1_replacement_after_min_working_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("4.1 Replacement only after FDW has worked for minimum of \
            __ day(s)"),
        choices=DAY_CHOICES
    )
    c4_1_5_replacement_deadline = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("4.1.5 Replacement FDW provided within __ month(s) from \
            date FDW returned"),
        choices=MONTH_CHOICES
    )
    c5_1_1_deployment_deadline = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.1 Deploy FDW to Employer within __ day(s) of date of \
            Service Agreement"),
        choices=DAY_CHOICES
    )
    c5_1_1_failed_deployment_refund = models.DecimalField(
        verbose_name=_("5.1.1 Failed FDW deployment refund amount"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    c5_1_2_refund_within_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.2 If Employer terminates Agreement, Employer entitled \
            to Service Fee refund within __ day(s)"),
        choices=DAY_CHOICES
    )
    c5_1_2_before_fdw_arrives_charge = models.DecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates BEFORE FDW arrives in \
            Singapore"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    c5_1_2_after_fdw_arrives_charge = models.DecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates AFTER FDW arrives in \
            Singapore"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    c5_2_2_can_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.2.2 If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=WEEK_CHOICES
    )
    c5_3_2_cannot_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.3.2 If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=WEEK_CHOICES
    )
    c6_4_per_day_food_accommodation_cost = models.DecimalField(
        verbose_name=_("6.4 Accommodation cost per day"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    c6_6_per_session_counselling_cost = models.DecimalField(
        verbose_name=_("6.6 Counselling cost per day"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    c9_1_independent_mediator_1 = models.CharField(
        verbose_name=_("9.1 Independent mediator #1"),
        max_length=40
    )
    c9_2_independent_mediator_2 = models.CharField(
        verbose_name=_("9.2 Independent mediator #2"),
        max_length=40
    )
    c13_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("13. Service Agreement termination notice (days)"),
        choices=DAY_CHOICES
    )

    # Employment Contract
    c3_1_fdw_salary = models.DecimalField(
        verbose_name=_("3.1 FDW monthly salary"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        help_text=_('FDW monthly salary in employment contract'),
    )
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
        choices=DAY_CHOICES
    )

    # Safety Agreement
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
    received_sip_assessment_checklist = models.BooleanField(
        verbose_name=_('Employer has received advisory letter and assessment checklist from SIP?'),
        choices=TrueFalseChoices(
            _('Yes, received'),
            _('Not received'),
        ),
        default=True,
        blank=True,
        null=True,
        help_text=_('For employers of first-time FDWs only')
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

    def save(self, *args, **kwargs):
        # Auto-increment document version number on every save
        self.version += 1

        # Spouse is required if application_scheme is 'SPOUS'
        self.spouse_required = True if self.application_scheme=='SPOUS' else False

        super().save(*args, **kwargs)

    def calc_admin_cost(self):
        # Method to calculate total administrative cost
        return (
            self.b1_service_fee
            + self.b2a_work_permit_application_collection
            + self.b2b_medical_examination_fee
            + self.b2c_security_bond_accident_insurance
            + self.b2d_indemnity_policy_reimbursement
            + self.b2e_home_service
            + self.b2f_counselling
            + self.b2g_sip
            + self.b2h_replacement_cost
            + self.b2i_work_permit_renewal
            + self.b2j1_other_services_fee
            + self.b2j2_other_services_fee
            + self.b2j3_other_services_fee
        )

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
            - self.ca_deposit
        )

        subsequent_transactions = EmployerPaymentTransaction.objects.filter(
            employer_doc=self
        )

        for transaction in subsequent_transactions:
            if transaction.transaction_type == 'ADD':
                balance += transaction.amount
            elif transaction.transaction_type == 'SUB':
                balance -= transaction.amount
        
        return balance

    def get_version(self):
        return str(self.version).zfill(4)

class EmployerDocSig(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_signatures_ed'
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

    # Optional signatures
    spouse_signature = models.TextField(
        verbose_name=_('Spouse Signature'),
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

    # Verification Tokens
    employer_slug = models.SlugField(
        max_length=36,
        default=uuid.uuid4,
        unique=True
    )
    employer_token = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    fdw_slug = models.SlugField(
        max_length=36,
        default=uuid.uuid4,
        unique=True
    )
    fdw_token = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    # Witnesses
    employer_witness_signature = models.TextField(
        verbose_name=_('Signature of Witness for Employer'),
        blank=True,
        null=True
    )
    employer_witness_name = models.CharField(
        verbose_name=_('Employer Witness Name'),
        max_length=40,
        blank=True,
        null=True
    )
    employer_witness_nric = models.CharField(
        verbose_name=_('Last 4 characters of NRIC/FIN'),
        max_length=4,
        blank=True,
        null=True
    )
    employer_witness_address_1 = models.CharField(
        verbose_name=_('Employer Witness Address Line 1'),
        max_length=100,
        blank=True,
        null=True
    )

    employer_witness_address_2 = models.CharField(
        verbose_name=_('Employer Witness Address Line 2'),
        max_length=50,
        blank=True,
        null=True
    )

    employer_witness_post_code = models.CharField(
        verbose_name=_('Employer Witness Postal Code'),
        max_length=25,
        blank=True,
        null=True
    )

    fdw_witness_signature = models.TextField(
        verbose_name=_('Signature of Witness for FDW'),
        blank=True,
        null=True
    )
    fdw_witness_name = models.CharField(
        verbose_name=_('FDW Witness Name'),
        max_length=40,
        blank=True,
        null=True
    )
    fdw_witness_nric = models.CharField(
        verbose_name=_('Last 4 characters of NRIC/FIN'),
        max_length=4,
        blank=True,
        null=True
    )
    agency_staff_witness_signature = models.TextField(
        verbose_name=_('Signature of Witness for Agency Staff Member'),
        blank=True,
        null=True
    )
    agency_staff_witness_name = models.CharField(
        verbose_name=_('Agency Staff Memeber Witness Name'),
        max_length=40,
        blank=True,
        null=True
    )
    agency_staff_witness_nric = models.CharField(
        verbose_name=_('Last 4 characters of NRIC/FIN'),
        max_length=4,
        blank=True,
        null=True
    )

class EmployerDocMaidStatus(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_maidstatus_ed'
    )
    fdw_work_commencement_date = models.DateField(
        verbose_name=_('Deployment Date'),
        blank=True,
        null=True
    )
    ipa_approval_date = models.DateField(
        verbose_name=_('In Principle Approval (IPA) Date'),
        blank=True,
        null=True
    )
    security_bond_approval_date = models.DateField(
        verbose_name=_('Security Bond Approval Date'),
        blank=True,
        null=True
    )
    arrival_date = models.DateField(
        verbose_name=_('FDW Arrival Date'),
        blank=True,
        null=True
    )
    thumb_print_date = models.DateField(
        verbose_name=_('FDW Thumb Print Date'),
        blank=True,
        null=True
    )
    sip_date = models.DateField(
        verbose_name=_('Settling-In Programme (SIP) Date'),
        blank=True,
        null=True
    )
    work_permit_no = models.CharField(
        verbose_name=_('Work Permit Number'),
        max_length=20,
        blank=True,
        null=True
    )
    is_deployed = models.BooleanField(
        verbose_name=_('deployed status'),
        default=False,
        choices=TrueFalseChoices(
            _('Yes, deployed'),
            _('No, not yet deployed'),
        ),
        help_text=_('''
            Marking FDW status as deployed will move case from status summary
            to sales summary.
        '''),
    )

class JobOrder(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_joborder_ed'
    )
    slug = models.SlugField(
        max_length=100,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    job_order_pdf = models.FileField(
        verbose_name=_('Upload Job Order (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

class PdfArchive(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_pdfarchive_ed'
    )
    f01_service_fee_schedule = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f03_service_agreement = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f04_employment_contract = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f05_repayment_schedule = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f06_rest_day_agreement = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f08_handover_checklist = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f09_transfer_consent = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f10_work_pass_authorisation = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f11_security_bond = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f12_fdw_work_permit = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f13_income_tax_declaration = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )
    f14_safety_agreement = models.FileField(
        upload_to=generate_archive_path,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        blank=True,
        null=True,
    )

class EmployerPaymentTransaction(models.Model):
    TRANSACTION_CHOICES = (
        ('SUB', _('Repayment')),
        ('ADD', _('New charge')),
    )
    employer_doc = models.ForeignKey(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_repayment_ed'
    )
    amount = models.DecimalField(
        verbose_name=_("Amount"),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
    )
    transaction_type = models.CharField(
        verbose_name=_("Type of transaction"),
        max_length=3,
        blank=False,
        choices=TRANSACTION_CHOICES,
        default=TRANSACTION_CHOICES[0][0]
    )
    transaction_date = models.DateField()
