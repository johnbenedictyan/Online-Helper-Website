import os
import uuid
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from accounts.models import PotentialEmployer
from agency.models import AgencyEmployee
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from maid.constants import TypeOfMaidChoices
from maid.models import Maid
from onlinemaid.constants import TrueFalseChoices
from onlinemaid.fields import (CustomBinaryField, GenderCharField,
                               MaritalStatusCharField, NationalityCharField,
                               NullableBooleanField, NullableCharField,
                               NullableDateField, NullableGenderCharField,
                               NullableMaritalStatusCharField,
                               NullableNationalityCharField)
from onlinemaid.helper_functions import decrypt_string, is_married
from onlinemaid.storage_backends import EmployerDocumentationStorage

# App Imports
from .constants import (NUMBER_OF_WORK_DAYS_IN_MONTH, CaseStatusChoices,
                        DayChoices, DayOfWeekChoices,
                        EmployerTypeOfApplicantChoices, HouseholdIdTypeChoices,
                        IncomeChoices, MonthChoices, RelationshipChoices,
                        ResidentialStatusPartialChoices, WeekChoices)
from .fields import (CustomMoneyDecimalField,
                     NullableResidentialStatusCharField,
                     ResidentialStatusCharField)
from .helper_functions import (is_applicant_joint_applicant,
                               is_applicant_sponsor, is_applicant_spouse,
                               is_local)

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


class ReceiptMaster(models.Model):
    number = models.PositiveBigIntegerField(
        verbose_name=_('Running Count of the receipt numbers'),
        editable=False,
        default=0
    )

    def get_running_number(self):
        return self.number

    def set_increment_running_number(self):
        self.number += 1
        self.save()

# Employer e-Documentation Models


class Employer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    potential_employer = models.ForeignKey(
        PotentialEmployer,
        related_name='employers',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    applicant_type = models.CharField(
        verbose_name=_("Type of Applicant"),
        max_length=6,
        choices=EmployerTypeOfApplicantChoices.choices,
        default=EmployerTypeOfApplicantChoices.SINGLE
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
        ''')
    )

    agency_employee = models.ForeignKey(
        AgencyEmployee,
        verbose_name=_('Assigned EA Personnel'),
        on_delete=models.RESTRICT
    )

    # Employer Information
    employer_name = models.CharField(
        verbose_name=_('Employer Name'),
        max_length=40
    )

    employer_gender = GenderCharField(
        verbose_name=_("Employer gender")
    )

    employer_mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$',  # Singapore mobile numbers
                message=_('Please enter a valid mobile number')
            )
        ]
    )

    employer_home_number = NullableCharField(
        verbose_name=_('Home Tel Number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[6][0-9]{7}$',  # Singapore landline numbers
                message=_('Please enter a valid home telephone number')
            )
        ]
    )

    employer_email = models.EmailField(
        verbose_name=_('Email Address')
    )

    employer_address_1 = models.CharField(
        verbose_name=_('Address Line 1'),
        max_length=100
    )

    employer_address_2 = NullableCharField(
        verbose_name=_('Address Line 2'),
        max_length=50
    )

    employer_post_code = models.CharField(
        verbose_name=_('Postal Code'),
        max_length=25
    )

    employer_date_of_birth = models.DateField(
        verbose_name=_('Employer date of birth')
    )

    employer_nationality = NationalityCharField(
        verbose_name=_("Employer nationality/citizenship")
    )

    employer_residential_status = ResidentialStatusCharField(
        verbose_name=_("Employer residential status")
    )

    employer_nric_num = CustomBinaryField(
        verbose_name=_('Employer NRIC')
    )

    employer_nric_nonce = CustomBinaryField()

    employer_nric_tag = CustomBinaryField()

    employer_fin_num = CustomBinaryField(
        verbose_name=_('Employer FIN')
    )

    employer_fin_nonce = CustomBinaryField()

    employer_fin_tag = CustomBinaryField()

    employer_passport_num = CustomBinaryField(
        verbose_name=_('Employer passport')
    )

    employer_passport_nonce = CustomBinaryField()

    employer_passport_tag = CustomBinaryField()

    employer_passport_date = NullableDateField(
        verbose_name=_('Employer passport expiry date')
    )

    employer_marital_status = NullableMaritalStatusCharField(
        verbose_name=_("Employer marital status")
    )

    employer_marriage_sg_registered = NullableBooleanField(
        verbose_name=_('Employer marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Employer's marriage registered in Singapore?
        ''')
    )

    # Employer Spouse
    spouse_name = NullableCharField(
        verbose_name=_("Spouse's Name"),
        max_length=40,
        default=None
    )

    spouse_gender = NullableGenderCharField(
        verbose_name=_("Spouse's gender")
    )

    spouse_date_of_birth = NullableDateField(
        verbose_name=_("Spouse's date of birth")
    )

    spouse_nationality = NullableNationalityCharField(
        verbose_name=_("Spouse's nationality/citizenship")
    )

    spouse_residential_status = NullableResidentialStatusCharField(
        verbose_name=_("Spouse's residential status")
    )

    spouse_nric_num = CustomBinaryField(
        verbose_name=_("Spouse's NRIC")
    )

    spouse_nric_nonce = CustomBinaryField()

    spouse_nric_tag = CustomBinaryField()

    spouse_fin_num = CustomBinaryField(
        verbose_name=_("Spouse's FIN")
    )

    spouse_fin_nonce = CustomBinaryField()

    spouse_fin_tag = CustomBinaryField()

    spouse_passport_num = CustomBinaryField(
        verbose_name=_("Spouse's Passport No")
    )

    spouse_passport_nonce = CustomBinaryField()

    spouse_passport_tag = CustomBinaryField()

    spouse_passport_date = NullableDateField(
        verbose_name=_("Spouse's Passport Expiry Date")
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
        if padded:
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
        if padded:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

    def get_employer_passport_full(self):
        return decrypt_string(
            self.employer_passport_num,
            settings.ENCRYPTION_KEY,
            self.employer_passport_nonce,
            self.employer_passport_tag,
        )

    def get_mobile_partial_sg(self):
        return '+65 ' + self.employer_mobile_number[:4] + ' ' + 'x'*4

    def get_email_partial(self):
        return self.employer_email[:3] + '_'*8 + self.employer_email[-3:]

    def get_employer_spouse_nric_full(self):
        return decrypt_string(
            self.spouse_nric_num,
            settings.ENCRYPTION_KEY,
            self.spouse_nric_nonce,
            self.spouse_nric_tag,
        )

    def get_employer_spouse_nric_partial(self, padded=True):
        plaintext = self.get_employer_spouse_nric_full()
        if padded:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

    def get_employer_spouse_fin_full(self):
        return decrypt_string(
            self.spouse_fin_num,
            settings.ENCRYPTION_KEY,
            self.spouse_fin_nonce,
            self.spouse_fin_tag,
        )

    def get_employer_spouse_fin_partial(self, padded=True):
        plaintext = self.get_employer_spouse_fin_full()
        if padded:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

    def get_employer_spouse_passport_full(self):
        return decrypt_string(
            self.spouse_passport_num,
            settings.ENCRYPTION_KEY,
            self.spouse_passport_nonce,
            self.spouse_passport_tag,
        )

    def set_potential_employer_relation(self, new_email):
        try:
            potential_employer = PotentialEmployer.objects.get(
                user__email=new_email
            )
        except PotentialEmployer.DoesNotExist:
            pass
        else:
            self.potential_employer = potential_employer
            self.save()

    def get_details_missing_spouse(self):
        error_msg_list = []

        if (
            is_married(self.employer_marital_status) or
            is_applicant_spouse(self.applicant_type)
        ):
            mandatory_fields = [
                'spouse_name',
                'spouse_gender',
                'spouse_date_of_birth',
                'spouse_nationality',
                'spouse_residential_status',
            ]

            for field in mandatory_fields:
                if not getattr(self, field):
                    error_msg_list.append(field)

            if is_local(self.spouse_residential_status):
                if not self.get_employer_spouse_nric_full():
                    error_msg_list.append('spouse_nric_num')
            else:
                if not self.get_employer_spouse_fin_full():
                    error_msg_list.append('spouse_fin_num')
                if not self.get_employer_spouse_passport_full():
                    error_msg_list.append('spouse_passport_num')
                if not self.spouse_passport_date:
                    error_msg_list.append('spouse_passport_date')

        return error_msg_list

    def get_details_missing_employer(self):
        # Retrieve verbose name ->
        # self._meta.get_field('field_name_str').verbose_name
        error_msg_list = []

        if is_local(self.employer_residential_status):
            if not self.get_employer_nric_full():
                error_msg_list.append('employer_nric_num')
        else:
            if not self.get_employer_fin_full():
                error_msg_list.append('employer_fin_num')
            if not self.get_employer_passport_full():
                error_msg_list.append('employer_passport_num')
            if not self.employer_passport_date:
                error_msg_list.append('employer_passport_date')

        # Check spouse details completeness
        error_msg_list += self.get_details_missing_spouse()

        if is_applicant_sponsor(self.applicant_type):
            if hasattr(self, 'rn_sponsor_employer'):
                m_s = self.rn_sponsor_employer.get_details_missing_sponsors()
                error_msg_list += m_s
            else:
                error_msg_list.append('rn_sponsor_employer')

        elif is_applicant_joint_applicant(self.applicant_type):
            if hasattr(self, 'rn_ja_employer'):
                m_ja = self.rn_ja_employer.get_details_missing_joint_applicant()
                error_msg_list += m_ja
            else:
                error_msg_list.append('rn_ja_employer')

        if not hasattr(self, 'rn_income_employer'):
            error_msg_list.append('rn_income_employer')

        if (
            self.household_details_required and
            not self.rn_household_employer.all().count()
        ):
            error_msg_list.append('rn_household_employer')

        return error_msg_list

    def get_income_obj(self):
        try:
            income_obj = self.rn_income_employer
        except ObjectDoesNotExist:
            pass
        else:
            return income_obj

    def get_sponsor_obj(self):
        try:
            sponsor_obj = self.rn_sponsor_employer
        except ObjectDoesNotExist:
            pass
        else:
            return sponsor_obj

    def get_joint_applicant_obj(self):
        try:
            joint_applicant_obj = self.rn_ja_employer
        except ObjectDoesNotExist:
            pass
        else:
            return joint_applicant_obj

    def __str__(self) -> str:
        return self.employer_name

# Sponsors


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
        choices=RelationshipChoices.choices,
        default=RelationshipChoices.DAUGHTER
    )
    sponsor_1_name = models.CharField(
        verbose_name=_('Sponsor 1 Name'),
        max_length=40
    )
    sponsor_1_gender = GenderCharField(
        verbose_name=_("Sponsor 1 gender")
    )
    sponsor_1_date_of_birth = models.DateField(
        verbose_name=_('Sponsor 1 date of birth')
    )
    sponsor_1_nric_num = models.BinaryField(
        verbose_name=_('Sponsor 1 NRIC'),
        editable=True
    )
    sponsor_1_nric_nonce = models.BinaryField(
        editable=True
    )
    sponsor_1_nric_tag = models.BinaryField(
        editable=True
    )
    sponsor_1_nationality = NationalityCharField(
        verbose_name=_("Sponsor 1 nationality/citizenship")
    )
    sponsor_1_residential_status = models.CharField(
        verbose_name=_("Sponsor 1 residential status"),
        max_length=2,
        choices=ResidentialStatusPartialChoices.choices,
        default=ResidentialStatusPartialChoices.SC
    )
    sponsor_1_mobile_number = models.CharField(
        verbose_name=_('Sponsor 1 mobile number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$',  # Singapore mobile numbers
                message=_('Please enter a valid contact number')
            )
        ]
    )
    sponsor_1_email = models.EmailField(
        verbose_name=_('Sponsor 1 email address')
    )
    sponsor_1_address_1 = models.CharField(
        verbose_name=_('Sponsor 1 Address Line 1'),
        max_length=100
    )
    sponsor_1_address_2 = NullableCharField(
        verbose_name=_('Sponsor 1 Address Line 2'),
        max_length=50
    )
    sponsor_1_post_code = models.CharField(
        verbose_name=_('Sponsor 1 Postal Code'),
        max_length=25
    )
    sponsor_1_marital_status = MaritalStatusCharField(
        verbose_name=_("Sponsor 1 marital status")
    )

    # Sponsor 1 spouse details
    sponsor_1_marriage_sg_registered = NullableBooleanField(
        verbose_name=_('Sponsor 1 marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Sponsor 1's marriage registered in Singapore?
        ''')
    )
    sponsor_1_spouse_name = NullableCharField(
        verbose_name=_('Sponsor 1 spouse name'),
        max_length=40
    )
    sponsor_1_spouse_gender = NullableGenderCharField(
        verbose_name=_("Sponsor 1 spouse gender")
    )
    sponsor_1_spouse_date_of_birth = NullableDateField(
        verbose_name=_('Sponsor 1 spouse date of birth')
    )
    sponsor_1_spouse_nationality = NullableNationalityCharField(
        verbose_name=_("Sponsor 1 spouse nationality/citizenship")
    )
    sponsor_1_spouse_residential_status = NullableResidentialStatusCharField(
        verbose_name=_("Sponsor 1 spouse residential status")
    )
    sponsor_1_spouse_nric_num = CustomBinaryField(
        verbose_name=_('Sponsor 1 spouse NRIC')
    )
    sponsor_1_spouse_nric_nonce = CustomBinaryField()
    sponsor_1_spouse_nric_tag = CustomBinaryField()
    sponsor_1_spouse_fin_num = CustomBinaryField(
        verbose_name=_('Sponsor 1 spouse FIN')
    )
    sponsor_1_spouse_fin_nonce = CustomBinaryField()
    sponsor_1_spouse_fin_tag = CustomBinaryField()
    sponsor_1_spouse_passport_num = CustomBinaryField(
        verbose_name=_('Sponsor 1 spouse passport')
    )
    sponsor_1_spouse_passport_nonce = CustomBinaryField()
    sponsor_1_spouse_passport_tag = CustomBinaryField()
    sponsor_1_spouse_passport_date = NullableDateField(
        verbose_name=_('Sponsor 1 spouse passport expiry date')
    )

    # Sponsor required?
    sponsor_2_required = models.BooleanField(
        verbose_name=_('Do you need to add Sponsor 2?'),
        default=False,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        )
    )

    # Sponsor 2 details
    sponsor_2_relationship = NullableCharField(
        verbose_name=_("Sponsor 2 relationship with Employer"),
        max_length=30,
        choices=RelationshipChoices.choices,
        default=RelationshipChoices.DAUGHTER
    )
    sponsor_2_name = NullableCharField(
        verbose_name=_('Sponsor 2 Name'),
        max_length=40
    )
    sponsor_2_gender = NullableGenderCharField(
        verbose_name=_("Sponsor 2 gender")
    )
    sponsor_2_date_of_birth = NullableDateField(
        verbose_name=_('Sponsor 2 date of birth')
    )
    sponsor_2_nric_num = CustomBinaryField(
        verbose_name=_('Sponsor 2 NRIC')
    )
    sponsor_2_nric_nonce = CustomBinaryField()
    sponsor_2_nric_tag = CustomBinaryField()
    sponsor_2_nationality = NullableNationalityCharField(
        verbose_name=_("Sponsor 2 nationality/citizenship")
    )
    sponsor_2_residential_status = NullableCharField(
        verbose_name=_("Sponsor 2 residential status"),
        max_length=2,
        choices=ResidentialStatusPartialChoices.choices,
        default=ResidentialStatusPartialChoices.SC
    )
    sponsor_2_mobile_number = NullableCharField(
        verbose_name=_('Sponsor 2 mobile number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$',  # Singapore mobile numbers
                message=_('Please enter a valid contact number')
            )
        ]
    )
    sponsor_2_email = models.EmailField(
        verbose_name=_('Sponsor 2 email address'),
        blank=True,
        null=True
    )
    sponsor_2_address_1 = NullableCharField(
        verbose_name=_('Sponsor 2 Address Line 1'),
        max_length=100
    )
    sponsor_2_address_2 = NullableCharField(
        verbose_name=_('Sponsor 2 Address Line 2'),
        max_length=50
    )
    sponsor_2_post_code = NullableCharField(
        verbose_name=_('Sponsor 2 Postal Code'),
        max_length=25
    )
    sponsor_2_marital_status = NullableMaritalStatusCharField(
        verbose_name=_("Sponsor 2 marital status")
    )
    sponsor_2_marriage_sg_registered = NullableBooleanField(
        verbose_name=_('Sponsor 2 marriage registered in SG?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Sponsor 2's marriage registered in Singapore?
        ''')
    )

    # Sponsor 2 spouse details
    sponsor_2_spouse_name = NullableCharField(
        verbose_name=_('Sponsor 2 spouse name'),
        max_length=40
    )
    sponsor_2_spouse_gender = NullableGenderCharField(
        verbose_name=_("Sponsor 2 spouse gender")
    )
    sponsor_2_spouse_date_of_birth = NullableDateField(
        verbose_name=_('Sponsor 2 spouse date of birth')
    )
    sponsor_2_spouse_nationality = NullableNationalityCharField(
        verbose_name=_("Sponsor 2 spouse nationality/citizenship")
    )
    sponsor_2_spouse_residential_status = NullableResidentialStatusCharField(
        verbose_name=_("Sponsor 2 spouse residential status")
    )
    sponsor_2_spouse_nric_num = CustomBinaryField(
        verbose_name=_('Sponsor 2 spouse NRIC')
    )
    sponsor_2_spouse_nric_nonce = CustomBinaryField()
    sponsor_2_spouse_nric_tag = CustomBinaryField()
    sponsor_2_spouse_fin_num = CustomBinaryField(
        verbose_name=_('Sponsor 2 spouse FIN')
    )
    sponsor_2_spouse_fin_nonce = CustomBinaryField()
    sponsor_2_spouse_fin_tag = CustomBinaryField()
    sponsor_2_spouse_passport_num = CustomBinaryField(
        verbose_name=_('Sponsor 2 spouse passport')
    )
    sponsor_2_spouse_passport_nonce = CustomBinaryField()
    sponsor_2_spouse_passport_tag = CustomBinaryField()
    sponsor_2_spouse_passport_date = NullableDateField(
        verbose_name=_('Sponsor 2 spouse passport expiry date')
    )

    def get_sponsor_1_nric_full(self):
        return decrypt_string(
            self.sponsor_1_nric_num,
            settings.ENCRYPTION_KEY,
            self.sponsor_1_nric_nonce,
            self.sponsor_1_nric_tag,
        )

    def get_sponsor_1_nric_partial(self, padded=True):
        plaintext = self.get_sponsor_1_nric_full()
        if padded:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

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

    def get_sponsor_2_nric_partial(self, padded=True):
        plaintext = self.get_sponsor_2_nric_full()
        if padded:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

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

    def get_details_missing_sponsor_2_spouse(self):
        error_msg_list = []

        if is_married(self.sponsor_2_marital_status):
            mandatory_fields = [
                'sponsor_2_spouse_name',
                'sponsor_2_spouse_gender',
                'sponsor_2_spouse_date_of_birth',
                'sponsor_2_spouse_nationality',
                'sponsor_2_spouse_residential_status',
            ]

            for field in mandatory_fields:
                if not getattr(self, field):
                    error_msg_list.append(field)

            if is_local(self.sponsor_2_spouse_residential_status):
                if not self.get_sponsor_2_spouse_nric_full():
                    error_msg_list.append('sponsor_2_spouse_nric_num')
            else:
                if not self.get_sponsor_2_spouse_fin_full():
                    error_msg_list.append('sponsor_2_spouse_fin_num')
                if not self.get_sponsor_2_spouse_passport_full():
                    error_msg_list.append('sponsor_2_spouse_passport_num')
                if not self.sponsor_2_spouse_passport_date:
                    error_msg_list.append('sponsor_2_spouse_passport_date')

        return error_msg_list

    def get_details_missing_sponsor_2(self):
        error_msg_list = []

        if self.sponsor_2_required:
            mandatory_fields = [
                'sponsor_2_relationship',
                'sponsor_2_name',
                'sponsor_2_gender',
                'sponsor_2_date_of_birth',
                'sponsor_2_nationality',
                'sponsor_2_residential_status',
                'sponsor_2_mobile_number',
                'sponsor_2_email',
                'sponsor_2_address_1',
                'sponsor_2_post_code',
                'sponsor_2_marital_status',
            ]

            for field in mandatory_fields:
                if not getattr(self, field):
                    error_msg_list.append(f'rn_sponsor_employer.{field}')

            if not self.get_sponsor_2_nric_full():
                error_msg_list.append('rn_sponsor_employer.sponsor_2_nric_num')

            error_msg_list += self.get_details_missing_sponsor_2_spouse()

        return error_msg_list

    def get_details_missing_sponsor_1_spouse(self):
        error_msg_list = []

        if is_married(self.sponsor_1_marital_status):
            mandatory_fields = [
                'sponsor_1_spouse_name',
                'sponsor_1_spouse_gender',
                'sponsor_1_spouse_date_of_birth',
                'sponsor_1_spouse_nationality',
                'sponsor_1_spouse_residential_status',
            ]

            for field in mandatory_fields:
                if not getattr(self, field):
                    error_msg_list.append(field)

            if is_local(self.sponsor_1_spouse_residential_status):
                if not self.get_sponsor_1_spouse_nric_full():
                    error_msg_list.append('sponsor_1_spouse_nric_num')
            else:
                if not self.get_sponsor_1_spouse_fin_full():
                    error_msg_list.append('sponsor_1_spouse_fin_num')
                if not self.get_sponsor_1_spouse_passport_full():
                    error_msg_list.append('sponsor_1_spouse_passport_num')
                if not self.sponsor_1_spouse_passport_date:
                    error_msg_list.append('sponsor_1_spouse_passport_date')

        return error_msg_list

    def get_details_missing_sponsors(self):
        error_msg_list = []
        error_msg_list += self.get_details_missing_sponsor_1_spouse()
        error_msg_list += self.get_details_missing_sponsor_2()
        return error_msg_list

# Joint Applicants


class EmployerJointApplicant(models.Model):
    employer = models.OneToOneField(
        Employer,
        on_delete=models.CASCADE,
        related_name='rn_ja_employer'
    )
    joint_applicant_relationship = models.CharField(
        verbose_name=_("Joint applicant's relationship with Employer"),
        max_length=30,
        choices=RelationshipChoices.choices,
        default=RelationshipChoices.DAUGHTER
    )
    joint_applicant_name = models.CharField(
        verbose_name=_("Joint applicant's Name"),
        max_length=40
    )
    joint_applicant_gender = GenderCharField(
        verbose_name=_("Joint applicant's gender")
    )
    joint_applicant_date_of_birth = models.DateField(
        verbose_name=_("Joint applicant's date of birth")
    )
    joint_applicant_nric_num = models.BinaryField(
        verbose_name=_('Joint applicant NRIC'),
        editable=True
    )
    joint_applicant_nric_nonce = models.BinaryField(
        editable=True
    )
    joint_applicant_nric_tag = models.BinaryField(
        editable=True
    )
    joint_applicant_nationality = NationalityCharField(
        verbose_name=_("Joint applicant's nationality/citizenship")
    )
    joint_applicant_residential_status = models.CharField(
        verbose_name=_("Joint applicant's residential status"),
        max_length=2,
        choices=ResidentialStatusPartialChoices.choices,
        default=ResidentialStatusPartialChoices.SC
    )
    joint_applicant_address_1 = models.CharField(
        verbose_name=_("Joint applicant's Address Line 1"),
        max_length=100
    )
    joint_applicant_address_2 = NullableCharField(
        verbose_name=_("Joint applicant's Address Line 2"),
        max_length=50
    )
    joint_applicant_post_code = models.CharField(
        verbose_name=_("Joint applicant's Postal Code"),
        max_length=25
    )
    joint_applicant_marital_status = MaritalStatusCharField(
        verbose_name=_("Joint applicant's marital status")
    )
    joint_applicant_marriage_sg_registered = NullableBooleanField(
        verbose_name=_("Joint applicant's marriage registered in SG?"),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        ),
        help_text=_('''
            Was Joint applicant's marriage registered in Singapore?
        ''')
    )

    # Joint applicant's spouse details
    joint_applicant_spouse_name = NullableCharField(
        verbose_name=_("Joint applicant's spouse name"),
        max_length=40
    )
    joint_applicant_spouse_gender = NullableGenderCharField(
        verbose_name=_("Joint applicant's spouse gender")
    )
    joint_applicant_spouse_date_of_birth = NullableDateField(
        verbose_name=_("Joint applicant's spouse date of birth")
    )
    joint_applicant_spouse_nationality = NullableNationalityCharField(
        verbose_name=_("Joint applicant's spouse nationality/citizenship")
    )
    joint_applicant_spouse_residential_status = NullableResidentialStatusCharField(
        verbose_name=_("Joint applicant's spouse residential status")
    )
    joint_applicant_spouse_nric_num = models.BinaryField(
        verbose_name=_("Joint applicant's spouse NRIC"),
        editable=True,
        blank=True,
        null=True
    )
    joint_applicant_spouse_nric_nonce = CustomBinaryField()
    joint_applicant_spouse_nric_tag = CustomBinaryField()
    joint_applicant_spouse_fin_num = CustomBinaryField(
        verbose_name=_("Joint applicant's spouse FIN")
    )
    joint_applicant_spouse_fin_nonce = CustomBinaryField()
    joint_applicant_spouse_fin_tag = CustomBinaryField()
    joint_applicant_spouse_passport_num = CustomBinaryField(
        verbose_name=_("Joint applicant's spouse passport")
    )
    joint_applicant_spouse_passport_nonce = CustomBinaryField()
    joint_applicant_spouse_passport_tag = CustomBinaryField()
    joint_applicant_spouse_passport_date = NullableDateField(
        verbose_name=_("Joint applicant's spouse passport expiry date")
    )

    def get_joint_applicant_nric_full(self):
        return decrypt_string(
            self.joint_applicant_nric_num,
            settings.ENCRYPTION_KEY,
            self.joint_applicant_nric_nonce,
            self.joint_applicant_nric_tag,
        )

    def get_joint_applicant_nric_partial(self, padded=True):
        plaintext = self.get_joint_applicant_nric_full()
        if padded:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

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

    def get_details_missing_joint_applicant_spouse(self):
        error_msg_list = []

        if is_married(self.joint_applicant_marital_status):
            mandatory_fields = [
                'joint_applicant_spouse_name',
                'joint_applicant_spouse_gender',
                'joint_applicant_spouse_date_of_birth',
                'joint_applicant_spouse_nationality',
                'joint_applicant_spouse_residential_status',
            ]

            for field in mandatory_fields:
                if not getattr(self, field):
                    error_msg_list.append(field)

            if is_local(self.joint_applicant_spouse_residential_status):
                if not self.joint_applicant_spouse_nric_full():
                    error_msg_list.append('joint_applicant_spouse_nric_num')
            else:
                if not self.get_joint_applicant_spouse_fin_full():
                    error_msg_list.append('joint_applicant_spouse_fin_num')
                if not self.get_joint_applicant_spouse_passport_full():
                    error_msg_list.append(
                        'joint_applicant_spouse_passport_num'
                    )
                if not self.joint_applicant_spouse_passport_date:
                    error_msg_list.append(
                        'joint_applicant_spouse_passport_date'
                    )

        return error_msg_list

    def get_details_missing_joint_applicant(self):
        error_msg_list = []

        if is_local(self.joint_applicant_residential_status):
            if not self.get_joint_applicant_nric_full():
                error_msg_list.append('joint_applicant_nric_num')
        else:
            if not self.get_joint_applicant_fin_full():
                error_msg_list.append('joint_applicant_fin_num')
            if not self.get_joint_applicant_passport_full():
                error_msg_list.append('joint_applicant_passport_num')
            if not self.joint_applicant_passport_date:
                error_msg_list.append('joint_applicant_passport_date')

        error_msg_list += self.get_details_missing_joint_applicant_spouse()
        return error_msg_list


class EmployerIncome(models.Model):
    employer = models.OneToOneField(
        Employer,
        verbose_name=_("Name of Employer"),
        on_delete=models.CASCADE,
        related_name="rn_income_employer"
    )
    # Income Details
    worked_in_sg = models.BooleanField(
        verbose_name=_('Have you worked in Singapore for the last 2 Years?'),
        default=True,
        choices=TrueFalseChoices(
            _('Yes'),
            _('No'),
        )
    )
    monthly_income = models.PositiveSmallIntegerField(
        verbose_name=_("Monthly Income"),
        choices=IncomeChoices.choices,
        default=IncomeChoices.INCOME_3
    )


class EmployerHousehold(models.Model):
    employer = models.ForeignKey(
        Employer,
        verbose_name=_("Name of Employer"),
        on_delete=models.CASCADE,
        related_name="rn_household_employer"
    )
    # Household Details
    household_name = models.CharField(
        verbose_name=_("Household member's name"),
        max_length=40
    )
    household_id_type = models.CharField(
        verbose_name=_("Household member ID type"),
        max_length=8,
        choices=HouseholdIdTypeChoices.choices,
        # default=HouseholdIdTypeChoices.NRIC
    )
    household_id_num = models.BinaryField(
        verbose_name=_("Household member's ID number"),
        editable=True
    )
    household_id_nonce = models.BinaryField(
        editable=True
    )
    household_id_tag = models.BinaryField(
        editable=True
    )
    household_date_of_birth = models.DateField(
        verbose_name=_("Household member's date of birth")
    )
    household_relationship = models.CharField(
        verbose_name=_("Household member's relationship with Employer"),
        max_length=30,
        choices=RelationshipChoices.choices,
        # default=RelationshipChoices.DAUGHTER
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
        unique=True
    )
    version = models.PositiveSmallIntegerField(
        editable=False,
        default=0
    )

    # User input fields
    case_ref_no = models.CharField(
        verbose_name=_("Case Reference Number"),
        max_length=20,
        unique=True
    )
    agreement_date = models.DateField(
        verbose_name=_("Contract Date")
    )
    employer = models.ForeignKey(
        Employer,
        verbose_name=_("Name of Employer"),
        on_delete=models.CASCADE,
        related_name="rn_ed_employer"
    )
    fdw = models.ForeignKey(
        Maid,
        verbose_name=_("Name of FDW"),
        on_delete=models.RESTRICT
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
        choices=DayChoices.choices[0:9],
        default=4,
        help_text=_("FDW off-days a month per contract")
    )
    fdw_monthly_loan_repayment = CustomMoneyDecimalField(
        verbose_name=_("FDW Monthly Loan Repayment"),
        help_text=_("Should be less than basic salary")
    )
    fdw_off_day_of_week = models.PositiveSmallIntegerField(
        verbose_name=_("FDW Off Day Day of Week"),
        choices=DayOfWeekChoices.choices,
        default=DayOfWeekChoices.SUN
    )
    status = models.CharField(
        verbose_name=_('Case Status'),
        max_length=1,
        blank=True,
        choices=CaseStatusChoices.choices,
        default=CaseStatusChoices.LIVE
    )
    archived_agency_details = models.OneToOneField(
        'ArchivedAgencyDetails',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    archived_maid = models.OneToOneField(
        'ArchivedMaid',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    key_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    def __str__(self) -> str:
        return f'Case # {self.case_ref_no}'

    def save(self, *args, **kwargs):
        # Auto-increment document version number on every save
        # self.version += 1
        super().save(*args, **kwargs)

        # Create related CaseStatus object if it does not exist
        if not hasattr(self, 'rn_casestatus_ed'):
            CaseStatus.objects.create(employer_doc=self)

        # Create related CaseSignature object if it does not exist
        if not hasattr(self, 'rn_signatures_ed'):
            CaseSignature.objects.create(employer_doc=self)

    def get_version(self):
        return str(self.version).zfill(4)

    def get_case_type(self) -> str:
        app_type = self.employer.applicant_type
        if app_type == EmployerTypeOfApplicantChoices.SPONSOR:
            if self.employer.rn_sponsor_employer.sponsor_2_required:
                return 'SPONSR2'
            else:
                return 'SPONSR1'
        else:
            return app_type

    def get_per_off_day_compensation(self):
        return Decimal(
            self.fdw_salary/NUMBER_OF_WORK_DAYS_IN_MONTH
        ).quantize(
            Decimal('.01'),
            rounding=ROUND_HALF_UP
        )

    def get_fdw_off_day_of_week_display(self):
        if int(self.fdw_off_day_of_week) == DayOfWeekChoices.MON:
            return _('Monday')
        elif int(self.fdw_off_day_of_week) == DayOfWeekChoices.TUE:
            return _('Tuesday')
        elif int(self.fdw_off_day_of_week) == DayOfWeekChoices.WED:
            return _('Wednesday')
        elif int(self.fdw_off_day_of_week) == DayOfWeekChoices.THU:
            return _('Thursday')
        elif int(self.fdw_off_day_of_week) == DayOfWeekChoices.FRI:
            return _('Friday')
        elif int(self.fdw_off_day_of_week) == DayOfWeekChoices.SAT:
            return _('Saturday')
        else:
            return _('Sunday')

    def get_details_missing_case_pre_signing_1(self):
        error_msg_list = self.employer.get_details_missing_employer()

        if not hasattr(self, 'rn_servicefeeschedule_ed'):
            error_msg_list.append('rn_servicefeeschedule_ed')

        if not hasattr(self, 'rn_serviceagreement_ed'):
            error_msg_list.append('rn_serviceagreement_ed')

        if hasattr(self, 'rn_docupload_ed'):
            if not self.rn_docupload_ed.job_order_pdf:
                error_msg_list.append('rn_docupload_ed.job_order_pdf')
        else:
            error_msg_list.append('rn_docupload_ed')

        if not hasattr(self, 'rn_signatures_ed'):
            error_msg_list.append('rn_signatures_ed')
        elif not self.rn_signatures_ed.agency_staff_signature:
            error_msg_list.append('agency_staff_signature')

        if (
            self.fdw.maid_type == TypeOfMaidChoices.NEW and
            not hasattr(self, 'rn_safetyagreement_ed')
        ):
            error_msg_list.append('rn_safetyagreement_ed')

        return error_msg_list

    def get_details_missing_case_pre_signing_2(self):
        error_msg_list = self.get_details_missing_case_pre_signing_1()

        if hasattr(self, 'rn_docupload_ed'):
            if not self.rn_docupload_ed.ipa_pdf:
                error_msg_list.append('rn_docupload_ed.ipa_pdf')
            if not self.rn_docupload_ed.medical_report_pdf:
                error_msg_list.append('rn_docupload_ed.medical_report_pdf')

        if hasattr(self, 'rn_casestatus_ed'):
            if not self.rn_casestatus_ed.fdw_work_commencement_date:
                error_msg_list.append(
                    'rn_casestatus_ed.fdw_work_commencement_date'
                )
        else:
            error_msg_list.append('rn_casestatus_ed')

        if not self.rn_maid_inventory.all().count():
            error_msg_list.append('rn_maid_inventory')

        if not self.fdw.get_passport_number():
            error_msg_list.append('fdw.passport_number')

        if not self.fdw.get_fdw_fin_full():
            error_msg_list.append('fdw.fin_number')

        return error_msg_list

    def get_stage(self):
        if self.rn_signatures_ed.employer_signature_1:
            return 1
        elif self.rn_signatures_ed.employer_signature_2:
            return 2
        else:
            return 0

    def set_archive(self):
        if not self.is_archived_doc():
            archived_agency_details = ArchivedAgencyDetails.objects.create(
                agency_name=self.employer.agency_employee.agency.name,
                agency_license_no=self.employer.agency_employee.agency.license_number,
                agency_address_line_1=self.employer.agency_employee.agency.get_main_branch().address_1,
                agency_address_line_2=self.employer.agency_employee.agency.get_main_branch().address_2,
                agency_postal_code=self.employer.agency_employee.agency.get_main_branch().postal_code,
                agency_employee_name=self.employer.agency_employee.name,
                agency_employee_ea_personnel_number=self.employer.agency_employee.ea_personnel_number,
                agency_employee_branch=self.employer.agency_employee.branch.name
            )
            archived_maid = ArchivedMaid.objects.create(
                name=self.fdw.name,
                nationality=self.fdw.get_country_of_origin_display(),
                passport_number=self.fdw.passport_number,
                passport_number_nonce=self.fdw.passport_number_nonce,
                passport_number_tag=self.fdw.passport_number_tag,
                fin_number=self.fdw.fin_number,
                fin_number_nonce=self.fdw.fin_number_nonce,
                fin_number_tag=self.fdw.fin_number_tag
            )

            self.archived_agency_details = archived_agency_details
            self.archived_maid = archived_maid

            self.status = CaseStatusChoices.ARCHIVED
            self.save()

    def set_increment_version_number(self):
        self.rn_signatures_ed.set_erase_signatures()
        self.version += 1
        self.save()

    @property
    def is_stage_0(self):
        return self.get_stage() == 0

    @property
    def is_stage_1(self):
        return self.get_stage() == 1

    @property
    def is_stage_2(self):
        return self.get_stage() == 2

    @property
    def is_archived_doc(self):
        return self.status == CaseStatusChoices.ARCHIVED


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
        default=True
    )
    fdw_replaced_name = NullableCharField(
        verbose_name=_("Name of FDW Replaced"),
        max_length=50
    )
    fdw_replaced_passport_num = CustomBinaryField(
        verbose_name=_('Passport No. of FDW Replaced')
    )
    fdw_replaced_passport_nonce = CustomBinaryField()
    fdw_replaced_passport_tag = CustomBinaryField()
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
    b2g1_other_services_description = NullableCharField(
        verbose_name=_("2g. Other services provided (i)"),
        max_length=40
    )
    b2g1_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (i)"),
        blank=True,
        null=True
    )
    b2g2_other_services_description = NullableCharField(
        verbose_name=_("2g. Other services provided (ii)"),
        max_length=40
    )
    b2g2_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (ii)"),
        blank=True,
        null=True
    )
    b2g3_other_services_description = NullableCharField(
        verbose_name=_("2g. Other services provided (iii)"),
        max_length=40
    )
    b2g3_other_services_fee = CustomMoneyDecimalField(
        verbose_name=_("2g. Other services fee (iii)"),
        blank=True,
        null=True
    )
    b2h_replacement_months = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("2h. Cost for replacement within __ month(s)"),
        choices=MonthChoices.choices,
        blank=True,
        null=True
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
    ca_deposit_date = NullableDateField(
        verbose_name=_('Deposit Paid Date')
    )
    ca_deposit_detail = NullableCharField(
        verbose_name=_("Deposit Payment Detail"),
        max_length=255
    )
    ca_remaining_payment_date = NullableDateField(
        verbose_name=_('Remaining Amount Paid Date')
    )
    ca_deposit_receipt_no = NullableCharField(
        max_length=255,
        verbose_name=_('Deposit Receipt No')
    )
    ca_remaining_payment_receipt_no = NullableCharField(
        max_length=255,
        verbose_name=_('Remaining Payment Receipt No')
    )
    ca_remaining_payment_detail = NullableCharField(
        verbose_name=_("Deposit Remaining Payment Detail"),
        max_length=255
    )
    ca_remaining_payment_amount = CustomMoneyDecimalField(
        verbose_name=_("Remaining Amount Paid"),
        default=0
    )

    def get_admin_cost(self):
        # Method to calculate total administrative cost
        total = 0
        fields = [
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

    def get_placement_fee(self):
        # Method to calculate placement fee
        return self.b3_agency_fee + self.employer_doc.fdw_loan

    def get_total_fee(self):
        # Method to calculate total fee
        return self.get_admin_cost() + self.get_placement_fee()

    def get_balance(self):
        # Method to calculate outstanding balance owed by employer
        balance = (
            self.get_admin_cost()
            + self.get_placement_fee()
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

    def get_receipt_no(self):
        receipt_master = ReceiptMaster()
        running_receipt_no = receipt_master.get_running_number()
        receipt_master.set_increment_running_number()
        month = datetime.now().strftime('%m')
        year = datetime.now().strftime('%Y')
        invoice_number = f'{running_receipt_no}/{month}/{year}'
        return invoice_number

    def set_invoice(self, invoice_type):
        if invoice_type == 'Deposit':
            self.ca_deposit_date = timezone.now()
            self.ca_deposit_receipt_no = self.get_receipt_no()
        else:
            self.ca_remaining_payment_date = timezone.now()
            self.ca_remaining_payment_amount = self.get_balance()
            # self.ca_remaining_payment_receipt_no = self.get_receipt_no()

        self.save()

    def set_deposit_invoice(self):
        self.set_invoice(invoice_type='Deposit')

    def set_remaining_invoice(self):
        self.set_invoice(invoice_type='Remaining Amount')


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
        choices=DayChoices.choices
    )
    c3_2_no_replacement_criteria_1 = NullableCharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (i)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_2 = NullableCharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (ii)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_3 = NullableCharField(
        verbose_name=_("3.2 No need to provide Employer with replacement FDW \
            if any of following circumstances (iii)"),
        max_length=100
    )
    c3_4_no_replacement_refund = CustomMoneyDecimalField(
        verbose_name=_("3.4 Refund if no replacement pursuant to Clause 3.1")
    )
    c4_1_number_of_replacements = models.PositiveSmallIntegerField(
        verbose_name=_("4.1 Number of replacement Employer is entitled to"),
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
        choices=MonthChoices.choices
    )
    c4_1_replacement_after_min_working_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("4.1 Replacement only after FDW has worked for minimum \
            of __ day(s)"),
        choices=DayChoices.choices
    )
    c4_1_5_replacement_deadline = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("4.1.5 Replacement must occur within __ month(s) \
            from FDW return date"),
        choices=MonthChoices.choices
    )
    c5_1_1_deployment_deadline = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.1 Deployment within __ day(s) of Service \
            Agreement date"),
        choices=DayChoices.choices
    )
    c5_1_1_failed_deployment_refund = CustomMoneyDecimalField(
        verbose_name=_("5.1.1 Failed deployment refund amount")
    )
    c5_1_2_refund_within_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("5.1.2 If Employer terminates Agreement, Employer \
            entitled to Service Fee refund within __ day(s)"),
        choices=DayChoices.choices
    )
    c5_1_2_before_fdw_arrives_charge = CustomMoneyDecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates BEFORE FDW \
            arrives in Singapore")
    )
    c5_1_2_after_fdw_arrives_charge = CustomMoneyDecimalField(
        verbose_name=_("5.1.2 Charge if Employer terminates AFTER FDW \
            arrives in Singapore")
    )
    c5_2_2_can_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.2.2 If new FDW deployed to Employer and former \
            FDW CAN be transferred to new employer, refund within __ week(s)"),
        choices=WeekChoices.choices
    )
    c5_3_2_cannot_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("5.3.2 If new FDW deployed to Employer and former FDW \
            CANNOT be transferred to new employer, refund within __ week(s)"),
        choices=WeekChoices.choices
    )
    c6_4_per_day_food_accommodation_cost = CustomMoneyDecimalField(
        verbose_name=_("6.4 Food and Accommodation cost per day")
    )
    c6_6_per_session_counselling_cost = CustomMoneyDecimalField(
        verbose_name=_("6.6 Counselling cost per day")
    )
    c9_1_independent_mediator_1 = NullableCharField(
        verbose_name=_("9.1 Independent mediator #1"),
        max_length=40
    )
    c9_2_independent_mediator_2 = NullableCharField(
        verbose_name=_("9.2 Independent mediator #2"),
        max_length=40
    )
    c13_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("13. Service Agreement termination notice (days)"),
        choices=DayChoices.choices
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
        default='OWN'
    )
    c4_1_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("4.1 Employment Contract termination notice (days)"),
        choices=DayChoices.choices
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
        default='HDB'
    )
    fdw_clean_window_exterior = models.BooleanField(
        verbose_name=_('Does Employer require FDW to clean window exterior?'),
        choices=TrueFalseChoices(
            _('Yes, clean window exterior'),
            _('No, not required'),
        ),
        default=False,
        help_text=_('If yes, must complete field (i).')
    )
    window_exterior_location = NullableCharField(
        verbose_name=_("(i) Location of window exterior"),
        max_length=6,
        choices=[
            ("GROUND", _("On the ground floor")),
            ("COMMON", _("Facing common corridor")),
            ("OTHER", _("Other")),
        ],
        help_text=_("If 'Other' is selected, must complete field (ii).")
    )
    grilles_installed_require_cleaning = NullableBooleanField(
        verbose_name=_(
            '(ii) Grilles installed on windows required to be cleaned by FDW?'
        ),
        choices=TrueFalseChoices(
            _('Yes, grilles installed require cleaning'),
            _('No, not required'),
        ),
        help_text=_('If yes, must complete field (iii).')
    )
    adult_supervision = NullableBooleanField(
        verbose_name=_(
            '(iii) Adult supervision when cleaning window exterior?'
        ),
        choices=TrueFalseChoices(
            _('Yes, adult supervision'),
            _('No supervision'),
        )
    )
    verifiy_employer_understands_window_cleaning = models.PositiveSmallIntegerField(
        verbose_name=_(
            "Verifiy employer understands window cleaning conditions"
        ),
        choices=[
            (
                1, _("FDW not required to clean window exterior")
            ),
            (
                2, _("FDW to clean only window exterior on ground floor")
            ),
            (
                3, _("FDW to clean only window exterior along common corridor")
            ),
            (
                4, _("Ensure grilles are locked and only cleaned under adult \
                    supervision")
            )
        ],
        default='not_required_to_clean_window_exterior'
    )

    def save(self):
        if not self.fdw_clean_window_exterior:
            self.window_exterior_location = None
            self.grilles_installed_require_cleaning = None
            self.adult_supervision = None

        elif not self.window_exterior_location == 'OTHER':
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
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    ipa_pdf = models.FileField(
        verbose_name=_('IPA (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    medical_report_pdf = models.FileField(
        verbose_name=_('Medical Report (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        storage=EmployerDocumentationStorage() if settings.USE_S3 else OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )


class MaidInventory(models.Model):
    item_name = models.CharField(
        verbose_name=_('Maid Inventory Item Name'),
        max_length=255
    )

    employer_doc = models.ForeignKey(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_maid_inventory'
    )

    def __str__(self) -> str:
        return self.item_name


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

    def get_employer_signature(self):
        if self.employer_signature_2:
            return self.employer_signature_2
        else:
            return self.employer_signature_1

    def set_erase_signatures(self):
        self.employer_signature_1 = None if self.employer_signature_1 else self.employer_signature_1
        self.fdw_signature = None if self.fdw_signature else self.fdw_signature
        self.agency_staff_signature = None if self.agency_staff_signature else self.agency_staff_signature
        self.employer_spouse_signature = None if self.employer_spouse_signature else self.employer_spouse_signature
        self.sponsor_1_signature = None if self.sponsor_1_signature else self.sponsor_1_signature
        self.sponsor_2_signature = None if self.sponsor_2_signature else self.sponsor_2_signature
        self.joint_applicant_signature = None if self.joint_applicant_signature else self.joint_applicant_signature
        self.save()


class CaseStatus(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_casestatus_ed'
    )
    ipa_approval_date = NullableDateField(
        verbose_name=_('In Principle Approval (IPA) Date')
    )
    arrival_date = NullableDateField(
        verbose_name=_('FDW Arrival Date')
    )
    shn_end_date = NullableDateField(
        verbose_name=_('SHN End Date')
    )
    thumb_print_date = NullableDateField(
        verbose_name=_('FDW Thumb Print Date')
    )
    fdw_work_commencement_date = NullableDateField(
        verbose_name=_('Deployment Date')
    )


class ArchivedAgencyDetails(models.Model):
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
        max_length=255
    )

    agency_employee_ea_personnel_number = models.CharField(
        verbose_name=_('EA personnel number'),
        max_length=50,
        default='NA',
        blank=True,
        help_text=_('Optional for non-personnel')
    )

    agency_employee_branch = models.CharField(
        verbose_name=_('Branch Name'),
        max_length=255
    )


class ArchivedMaid(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255
    )

    nationality = models.CharField(
        verbose_name=_('Nationality'),
        max_length=255
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

    fin_number = models.BinaryField(
        editable=True,
        blank=True
    )

    fin_number_nonce = models.BinaryField(
        editable=True,
        blank=True
    )

    fin_number_tag = models.BinaryField(
        editable=True,
        blank=True
    )
