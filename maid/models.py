# Imports from python

# Imports from django
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

# Imports from project
from onlinemaid.constants import TrueFalseChoices
from onlinemaid.helper_functions import (
    calculate_age, decrypt_string, humanise_time_duration
)
from onlinemaid.storage_backends import PublicMediaStorage

# Imports from other apps
from agency.models import Agency

# Imports from within the app
from .constants import (
    TypeOfMaidChoices, MaidCountryOfOrigin, MaidAssessmentChoices, 
    MaidPassportStatusChoices, MaidLanguageChoices, MaidResponsibilityChoices,
    MaritalStatusChoices, MaidReligionChoices, MaidEducationLevelChoices,
    MaidSkillsEvaluationMethod, MaidLoanDescriptionChoices, MaidStatusChoices
)

# Utiliy Classes and Functions

# Start of Models
class MaidResponsibility(models.Model):
    name = models.CharField(
        verbose_name=_('Name of maid\'s responsibility'),
        max_length=255,
        blank=False,
        choices=MaidResponsibilityChoices.choices
    )
    
    def __str__(self) -> str:
        return f'{self.get_name_display()}'

    def get_db_value(self):
        return self.name

class MaidLanguage(models.Model):
    language = models.CharField(
        verbose_name=_("Maid's spoken languages"),
        max_length=3,
        blank=False,
        choices=MaidLanguageChoices.choices
    )

    def __str__(self) -> str:
        return f'{self.get_language_display()}'

class Maid(models.Model):
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='maid'
    )

    reference_number = models.CharField(
        verbose_name=_('Reference Number'),
        max_length=255,
        blank=False
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=False,
        null=True
    )
    
    passport_number = models.BinaryField(
        editable=True
    )
    
    nonce = models.BinaryField(
        editable=True
    )
    
    tag = models.BinaryField(
        editable=True
    )

    photo = models.FileField(
        verbose_name=_('Maid Photo'),
        blank=False,
        null=True,
        storage=PublicMediaStorage() if settings.USE_S3 else None
    )

    maid_type = models.CharField(
        verbose_name=_('Maid Type'),
        max_length=3,
        blank=False,
        choices=TypeOfMaidChoices.choices,
        default=TypeOfMaidChoices.NEW
    )

    passport_status = models.BooleanField(
        verbose_name=_('Passport status'),
        max_length=1,
        blank=False,
        choices=MaidPassportStatusChoices.choices,
        default=MaidPassportStatusChoices.NOT_READY
    )
    
    passport_expiry = models.DateField(
        verbose_name=_('Passport Expiry Date'),
        blank=False
    )
    
    remarks = models.CharField(
        verbose_name=_('Remarks'),
        max_length=255,
        blank=False
    )
    
    languages = models.ManyToManyField(
        MaidLanguage
    )
    
    responsibilities = models.ManyToManyField(
        MaidResponsibility
    )
    
    skills_evaluation_method = models.CharField(
        verbose_name=_('Skills evaluation method'),
        max_length=4,
        blank=False,
        choices=MaidSkillsEvaluationMethod.choices,
        default=MaidSkillsEvaluationMethod.DECLARATION
    )

    created_on = models.DateTimeField(
        verbose_name=_('Created On'),
        auto_now_add=True,
        editable=False
    )

    updated_on = models.DateTimeField(
        verbose_name=_('Updated on'),
        auto_now=True,
        editable=False
    )

    status = models.CharField(
        verbose_name=_('Status'),
        max_length=4,
        blank=False,
        choices=MaidStatusChoices.choices,
        default=MaidStatusChoices.UNPUBLISHED
    )
    
    marital_status = models.CharField(
        verbose_name=_('Marital Status'),
        max_length=2,
        blank=False,
        choices=MaritalStatusChoices.choices,
        default=MaritalStatusChoices.SINGLE
    )

    number_of_children = models.PositiveSmallIntegerField(
        blank=False,
        default=0
    )

    age_of_children = models.CharField(
        verbose_name=_('Age of children'),
        max_length=50,
        blank=False,
        default='N.A'
    )

    number_of_siblings = models.PositiveSmallIntegerField(
        blank=False,
        default=0
    )

    country_of_origin = models.CharField(
        verbose_name=_('Country of Origin'),
        max_length=3,
        blank=False,
        null=True,
        choices=MaidCountryOfOrigin.choices
    )
    
    expected_salary = models.PositiveSmallIntegerField(
        verbose_name=_('Expected Salary'),
        blank=False,
        default=0
    )
    
    expected_days_off = models.PositiveSmallIntegerField(
        verbose_name=_('Expected No of Off Days'),
        blank=False,
        default=0
    )
    
    date_of_birth = models.DateField(
        verbose_name=_('Date of Birth'),
        blank=False,
        null=True
    )
    
    age = models.IntegerField(
        verbose_name=_('Age'),
        blank=False,
        null=True
    )

    height = models.DecimalField(
        verbose_name=_('Height'),
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200)
        ],
        blank=False
    )

    weight = models.DecimalField(
        verbose_name=_('Weight (in kg)'),
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        blank=False
    )
    
    place_of_birth = models.CharField(
        verbose_name=_('Place of birth'),
        max_length=25,
        blank=False,
        null=True
    )

    address_1 = models.CharField(
        verbose_name=_('Address 1'),
        max_length=100,
        blank=False,
        null=True
    )

    address_2 = models.CharField(
        verbose_name=_('Address 2'),
        max_length=100,
        blank=False,
        null=True
    )

    repatriation_airport = models.CharField(
        verbose_name=_('Repatriation airport'),
        max_length=100,
        blank=False
    )

    religion = models.CharField(
        verbose_name=_('Religion'),
        max_length=4,
        blank=False,
        choices=MaidReligionChoices.choices,
        default=MaidReligionChoices.NONE
    )
    
    contact_number = models.CharField(
        verbose_name=_('Contact number in home country'),
        max_length=30,
        blank=False,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid contact number')
            )
        ]
    )
    
    education_level = models.CharField(
        verbose_name=_('Education Level'),
        max_length=3,
        blank=False,
        choices=MaidEducationLevelChoices.choices,
        default=MaidEducationLevelChoices.HIGH_SCHOOL
    )
    
    def __str__(self):
        return self.reference_number + ' - ' + self.name

    def get_main_responsibility(self):
        main_responsibility = [
            i for i in self.responsibilities.all()
            if i.name != MaidResponsibilityChoices.MAID_RESP_GARDENING
            and i.name != MaidResponsibilityChoices.MAID_RESP_CARE_FOR_PETS
        ]
        return main_responsibility[0]

    def get_passport_number(self):
        plaintext = decrypt_string(
            self.passport_number,
            settings.ENCRYPTION_KEY,
            self.nonce,
            self.tag
        )
        return plaintext

    def get_age(self):
        today = timezone.now().date()
        try:
            birthday_current_year = self.date_of_birth.replace(
                year = today.year)
    
        # Raised when birth date is 29 February and the current year is not a
        # leap year
        except ValueError:
            birthday_current_year = self.date_of_birth.replace(
                year = today.year,
                month = self.date_of_birth.month + 1,
                day = 1
            )
    
        if birthday_current_year > today:
            return today.year - self.date_of_birth.year - 1
        else:
            return today.year - self.date_of_birth.year
        
class MaidWorkDuty(models.Model):
    class WorkDutyChoices(models.TextChoices):
        HOUSEWORK = 'H', _('Housework')
        HOUSEWORK_HDB = 'H_HDB', _('Housework (HDB)')
        HOUSEWORK_CONDO = 'H_CON', _('Housework (Condo)')
        HOUSEWORK_PRIVATE = 'H_PLP', _('Housework (Landed Property)')
        COOKING = 'CO', _('Cooking')
        COOKING_CHINESE = 'CO_C', _('Cooking (Chinese Food)')
        COOKING_INDIAN = 'CO_I', _('Cooking (Indian Food)')
        COOKING_MALAY = 'CO_M', _('Cooking (Malay Food)')
        CARE_INFANT_CHILD = 'CA_IC', _('Infant child care')
        CARE_ELDERLY = 'CA_E', _('Elderly care')
        CARE_DISABLED = 'CA_D', _('Disabled care')
        CARE_PETS = 'CA_P', _('Pet care')

    name = models.CharField(
        verbose_name=_("Maid's work duties"),
        max_length=5,
        blank=False,
        choices=WorkDutyChoices.choices
    )

    def __str__(self):
        return self.get_name_display()

## Models which have a one-to-many relationship with the maid model
class MaidFoodHandlingPreference(models.Model):
    class FoodPreferenceChoices(models.TextChoices):
        PORK = 'P', _('No pork')
        CHICKEN = 'C', _('No chicken')
        BEEF = 'B', _('No beef')
        SEAFOOD = 'S', _('No seafood')

    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='food_handling_preferences'
    )

    preference = models.CharField(
        verbose_name = _('Food preference'),
        max_length=1,
        blank=False,
        choices=FoodPreferenceChoices.choices,
        default=FoodPreferenceChoices.PORK
    )

class MaidDietaryRestriction(models.Model):
    class DietaryRestrictionChoices(models.TextChoices):
        PORK = 'P', _('No pork')
        CHICKEN = 'C', _('No chicken')
        BEEF = 'B', _('No beef')
        SEAFOOD = 'S', _('No seafood')

    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='dietary_restrictions'
    )

    restriction = models.CharField(
        verbose_name = _('Dietary restriction'),
        max_length=1,
        blank=False,
        choices=DietaryRestrictionChoices.choices,
        default=DietaryRestrictionChoices.PORK
    )

# class MaidEmploymentHistory(models.Model):
#     class MaidEmploymentCountry(models.TextChoices):
#         # https://en.wikipedia.org/wiki/ISO_3166-1
#         SINGAPORE = 'SGP', _('Singapore')
#         HONG_KONG = 'HKG', _('Hong Kong')
#         MALAYSIA = 'MYS', _('Malaysia')

#     maid = models.ForeignKey(
#         Maid,
#         on_delete=models.CASCADE,
#         related_name='employment_history'
#     )

#     start_date = models.DateField(
#         verbose_name="Past employment's start date"
#     )

#     end_date = models.DateField(
#         verbose_name="Past employment's end date"
#     )

#     country = models.CharField(
#         verbose_name=_("Country of employment"),
#         max_length=3,
#         blank=False,
#         choices=MaidEmploymentCountry.choices
#     )

#     work_duties = models.ManyToManyField(
#         MaidWorkDuty
#     )

#     def work_duration(self):
        # duration = self.end_date - self.start_date
        # return humanise_time_duration(duration)

class MaidLoanTransaction(models.Model):
    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='loan_transactions'
    )

    amount = models.DecimalField(
        verbose_name=_('Amount'),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        blank=False
    )

    description = models.CharField(
        verbose_name=_('Type of transaction'),
        max_length=3,
        blank=False,
        choices=MaidLoanDescriptionChoices.choices
    )

    remarks = models.TextField(
        verbose_name=_('Transaction Remarks'),
        blank=False
    )

    date = models.DateField(
        blank=False
    )

## Models which have a one-to-one relationship with the maid model 
class MaidEmploymentStatus(models.Model):
    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='employment_status'
    )

    ipa_approved = models.BooleanField(
        verbose_name=_('IPA approved'),
        blank=False,
        default=False
    )

    bond_date = models.DateField(
        verbose_name=_('Bond Date'),
        blank=False,
        null=True
    )

    sip_date = models.DateField(
        verbose_name=_('SIP Date'),
        blank=False,
        null=True
    )

    thumbprint_date = models.DateField(
        verbose_name=_('Thumbprint Date'),
        blank=False,
        null=True
    )

    deployment_date = models.DateField(
        verbose_name=_('Deployment Date'),
        blank=False,
        null=True
    )

class MaidInfantChildCare(models.Model):
    class InfantChildCareRemarksChoices(models.TextChoices):
        OWN_COUNTRY = 'OC', _('Experience in own country')
        OVERSEAS = 'OV', _('Experience in overseas')
        SINGAPORE = 'SG', _('Experience in Singapore')
        OWN_COUNTRY_SINGAPORE = 'OC_SG', _(
            'Experience in own country and Singapore'
        )
        OWN_COUNTRY_OVERSEAS = 'OC_O', _(
            'Experience in own country and overseas'
        )
        OWN_COUNTRY_OVERSEAS_SINGPAPORE = 'OC_O_SG', _(
            'Experience in own country, overseas and Singapore'
        )
        NO_EXP = 'NE', _('No experience, but willing to learn')
        NOT_WILLING = 'NW', _('Not willing to care for infants/children')
        OTHERS = 'OTH', _('Other remarks (Please specify)')

    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='infant_child_care'
    )

    assessment = models.IntegerField(
        verbose_name=_('Infant child care assessment'),
        blank=False,
        choices=MaidAssessmentChoices.choices,
        default=MaidAssessmentChoices.AVERAGE
    )

    willingness = models.BooleanField(
        verbose_name=_('Willingness for infant child care'),
        blank=False,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        default=True,
    )

    experience = models.BooleanField(
        verbose_name=_('Experience with infant child care'),
        blank=False,
        choices=TrueFalseChoices('Experience', 'No experience'),
        default=True,
    )

    remarks = models.CharField(
        verbose_name=_('Remarks for infant child care'),
        max_length=7,
        blank=False,
        choices=InfantChildCareRemarksChoices.choices,
        null=True
    )

    other_remarks = models.TextField(
        verbose_name=_('Other remarks for infant child care'),
        blank=True
    )

class MaidElderlyCare(models.Model):
    class ElderlyCareRemarksChoices(models.TextChoices):
        OWN_COUNTRY = 'OC', _('Experience in own country')
        OVERSEAS = 'OV', _('Experience in overseas')
        SINGAPORE = 'SG', _('Experience in Singapore')
        OWN_COUNTRY_SINGAPORE = 'OC_SG', _(
            'Experience in own country and Singapore'
        )
        OWN_COUNTRY_OVERSEAS = 'OC_O', _(
            'Experience in own country and overseas'
        )
        OWN_COUNTRY_OVERSEAS_SINGPAPORE = 'OC_O_SG', _(
            'Experience in own country, overseas and Singapore'
        )
        NO_EXP = 'NE', _('No experience, but willing to learn')
        NOT_WILLING = 'NW', _('Not willing to care for elderly')
        OTHERS = 'OTH', _('Other remarks (Please specify)')

    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='elderly_care'
    )

    assessment = models.IntegerField(
        verbose_name=_('Elderly care assessment'),
        blank=False,
        choices=MaidAssessmentChoices.choices,
        default=MaidAssessmentChoices.AVERAGE
    )

    willingness = models.BooleanField(
        verbose_name=_('Willingness for elderly care'),
        blank=False,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        default=True,
    )

    experience = models.BooleanField(
        verbose_name=_('Experience with elderly care'),
        blank=False,
        choices=TrueFalseChoices('Experience', 'No experience'),
        default=True,
    )

    remarks = models.CharField(
        verbose_name=_('Remarks for elderly care'),
        max_length=7,
        blank=False,
        choices=ElderlyCareRemarksChoices.choices,
        null=True
    )

    other_remarks = models.TextField(
        verbose_name=_('Other remarks for elderly care'),
        blank=True
    )

class MaidDisabledCare(models.Model):
    class DisabledCareRemarksChoices(models.TextChoices):
        OWN_COUNTRY = 'OC', _('Experience in own country')
        OVERSEAS = 'OV', _('Experience in overseas')
        SINGAPORE = 'SG', _('Experience in Singapore')
        OWN_COUNTRY_SINGAPORE = 'OC_SG', _(
            'Experience in own country and Singapore'
        )
        OWN_COUNTRY_OVERSEAS = 'OC_O', _(
            'Experience in own country and overseas'
        )
        OWN_COUNTRY_OVERSEAS_SINGPAPORE = 'OC_O_SG', _(
            'Experience in own country, overseas and Singapore'
        )
        NO_EXP = 'NE', _('No experience, but willing to learn')
        NOT_WILLING = 'NW', _('Not willing to care for disabled')
        OTHERS = 'OTH', _('Other remarks (Please specify)')

    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='disabled_care'
    )

    assessment = models.IntegerField(
        verbose_name=_('Disabled care assessment'),
        blank=False,
        choices=MaidAssessmentChoices.choices,
        default=MaidAssessmentChoices.AVERAGE
    )

    willingness = models.BooleanField(
        verbose_name=_('Willingness for disabled care'),
        blank=False,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        default=True,
    )

    experience = models.BooleanField(
        verbose_name=_('Experience with disabled care'),
        blank=False,
        choices=TrueFalseChoices('Experience', 'No experience'),
        default=True,
    )

    remarks = models.CharField(
        verbose_name=_('Remarks for disabled care'),
        max_length=7,
        blank=False,
        choices=DisabledCareRemarksChoices.choices,
        null=True
    )

    other_remarks = models.TextField(
        verbose_name=_('Other remarks for disabled care'),
        blank=True
    )

class MaidGeneralHousework(models.Model):
    class GeneralHouseworkRemarksChoices(models.TextChoices):
        CAN_DO_ALL_HOUSEWORK = 'CAN', _('Able to do all general housework')
        OTHERS = 'OTH', _('Other remarks (Please specify)')

    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='general_housework'
    )

    assessment = models.IntegerField(
        verbose_name=_('General housework assessment'),
        blank=False,
        choices=MaidAssessmentChoices.choices,
        default=MaidAssessmentChoices.AVERAGE
    )

    willingness = models.BooleanField(
        verbose_name=_('Willingness for general housework'),
        blank=False,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        default=True,
    )

    experience = models.BooleanField(
        verbose_name=_('Experience with general housework'),
        blank=False,
        choices=TrueFalseChoices('Experience', 'No experience'),
        default=True,
    )

    remarks = models.CharField(
        verbose_name=_('Remarks for general housework'),
        max_length=7,
        blank=False,
        choices=GeneralHouseworkRemarksChoices.choices,
        null=True
    )

    other_remarks = models.TextField(
        verbose_name=_('Other remarks for general housework'),
        blank=True
    )

class MaidCooking(models.Model):
    class CookingRemarksChoices(models.TextChoices):
        OWN_COUNTRY = 'OC', _('Able to cook own country\'s cuisine')
        CHINESE = 'C', _('Able to cook chinese cuisine')
        INDIAN = 'I', _('Able to cook indian cuisine')
        WESTERN = 'W', _('Able to cook western cuisine')
        OWN_COUNTRY_CHINSE = 'OC_C', _(
            'Able to cook own country\'s and chinese cuisine'
        )
        OWN_COUNTRY_INDIAN = 'OC_I', _(
            'Able to cook own country\'s and indian cuisine'
        )
        OWN_COUNTRY_WESTERN = 'OC_W', _(
            'Able to cook own country\'s and western cuisine'
        )
        CHINESE_INDIAN = 'C_I', _(
            'Able to cook chinese and indian cuisine'
        )
        CHINESE_WESTERN = 'C_W', _(
            'Able to cook chinese and western cuisine'
        )
        INDIAN_WESTERN = 'I_W', _(
            'Able to cook indian and western cuisine'
        )
        OWN_COUNTRY_CHINESE_INDIAN = 'OC_C_I', _(
            'Able to cook own country\'s, chinese and indian cuisine'
        )
        OWN_COUNTRY_CHINESE_WESTERN = 'OC_C_W', _(
            'Able to cook own country\'s, chinese and western cuisine'
        )
        OWN_COUNTRY_INDIAN_WESTERN = 'OC_I_W', _(
            'Able to cook own country\'s, indian and western cuisine'
        )
        CHINESE_INDIAN_WESTERN = 'C_I_W', _(
            'Able to cook chinese, indian and western cuisine'
        )
        OWN_COUNTRY_CHINESE_INDIAN_WESTERN = 'OC_C_I_W', _(
            'Able to cook own country\'s, chinese, indian and western cuisine'
        )
        OTHERS = 'OTH', _('Other remarks (Please specify)')

    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='cooking'
    )

    assessment = models.IntegerField(
        verbose_name=_('Cooking assessment'),
        blank=False,
        choices=MaidAssessmentChoices.choices,
        default=MaidAssessmentChoices.AVERAGE
    )

    willingness = models.BooleanField(
        verbose_name=_('Willingness for cooking'),
        blank=False,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        default=True,
    )

    experience = models.BooleanField(
        verbose_name=_('Experience with cooking'),
        blank=False,
        choices=TrueFalseChoices('Experience', 'No experience'),
        default=True,
    )

    remarks = models.CharField(
        verbose_name=_('Remarks for cooking'),
        max_length=8,
        blank=False,
        choices=CookingRemarksChoices.choices,
        null=True
    )

    other_remarks = models.TextField(
        verbose_name=_('Other remarks for cooking'),
        blank=True
    )

class MaidEmploymentHistory(models.Model):
    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='employment_history'
    )
    
    start_date_1 = models.DateField(
        verbose_name=_('Entry 1 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_1 = models.DateField(
        verbose_name=_('Entry 1 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_1 = models.CharField(
        verbose_name=_('Entry 1 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_1 = models.CharField(
        verbose_name=_('Entry 1 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_1 = models.CharField(
        verbose_name=_('Entry 1 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_1 = models.CharField(
        verbose_name=_('Entry 1 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_2 = models.DateField(
        verbose_name=_('Entry 2 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_2 = models.DateField(
        verbose_name=_('Entry 2 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_2 = models.CharField(
        verbose_name=_('Entry 2 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_2 = models.CharField(
        verbose_name=_('Entry 2 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_2 = models.CharField(
        verbose_name=_('Entry 2 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_2 = models.CharField(
        verbose_name=_('Entry 2 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_3 = models.DateField(
        verbose_name=_('Entry 3 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_3 = models.DateField(
        verbose_name=_('Entry 3 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_3 = models.CharField(
        verbose_name=_('Entry 3 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_3 = models.CharField(
        verbose_name=_('Entry 3 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_3 = models.CharField(
        verbose_name=_('Entry 3 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_3 = models.CharField(
        verbose_name=_('Entry 3 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_4 = models.DateField(
        verbose_name=_('Entry 4 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_4 = models.DateField(
        verbose_name=_('Entry 4 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_4 = models.CharField(
        verbose_name=_('Entry 4 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_4 = models.CharField(
        verbose_name=_('Entry 4 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_4 = models.CharField(
        verbose_name=_('Entry 4 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_4 = models.CharField(
        verbose_name=_('Entry 4 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_5 = models.DateField(
        verbose_name=_('Entry 5 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_5 = models.DateField(
        verbose_name=_('Entry 5 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_5 = models.CharField(
        verbose_name=_('Entry 5 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_5 = models.CharField(
        verbose_name=_('Entry 5 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_5 = models.CharField(
        verbose_name=_('Entry 5 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_5 = models.CharField(
        verbose_name=_('Entry 5 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_6 = models.DateField(
        verbose_name=_('Entry 6 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_6 = models.DateField(
        verbose_name=_('Entry 6 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_6 = models.CharField(
        verbose_name=_('Entry 6 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_6 = models.CharField(
        verbose_name=_('Entry 6 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_6 = models.CharField(
        verbose_name=_('Entry 6 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_6 = models.CharField(
        verbose_name=_('Entry 6 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_7 = models.DateField(
        verbose_name=_('Entry 7 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_7 = models.DateField(
        verbose_name=_('Entry 7 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_7 = models.CharField(
        verbose_name=_('Entry 7 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_7 = models.CharField(
        verbose_name=_('Entry 7 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_7 = models.CharField(
        verbose_name=_('Entry 7 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_7 = models.CharField(
        verbose_name=_('Entry 7 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_8 = models.DateField(
        verbose_name=_('Entry 8 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_8 = models.DateField(
        verbose_name=_('Entry 8 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_8 = models.CharField(
        verbose_name=_('Entry 8 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_8 = models.CharField(
        verbose_name=_('Entry 8 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_8 = models.CharField(
        verbose_name=_('Entry 8 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_8 = models.CharField(
        verbose_name=_('Entry 8 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_9 = models.DateField(
        verbose_name=_('Entry 9 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_9 = models.DateField(
        verbose_name=_('Entry 9 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_9 = models.CharField(
        verbose_name=_('Entry 9 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_9 = models.CharField(
        verbose_name=_('Entry 9 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_9 = models.CharField(
        verbose_name=_('Entry 9 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_9 = models.CharField(
        verbose_name=_('Entry 9 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    start_date_10 = models.DateField(
        verbose_name=_('Entry 10 - Start Date'),
        blank=True, 
        null=True
    )
    
    end_date_10 = models.DateField(
        verbose_name=_('Entry 10 - End Date'),
        blank=True, 
        null=True
    )
    
    employer_10 = models.CharField(
        verbose_name=_('Entry 10 - Country or Race of Employer'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    country_10 = models.CharField(
        verbose_name=_('Entry 10 - Country'),
        max_length=255,
        blank=True, 
        null=True
    )

    work_duties_10 = models.CharField(
        verbose_name=_('Entry 10 - Work Duties'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    reason_for_leaving_10 = models.CharField(
        verbose_name=_('Entry 10 - Reason for Leaving'),
        max_length=255,
        blank=True, 
        null=True
    )
    
    def work_duration(self, entry_number):
        duration = (
            self[
                f'end_date_{entry_number}'
            ] - self[
                f'start_date_{entry_number}'
            ]
        )
        return humanise_time_duration(duration)
    
# class MaidOtherCare(models.Model):
#     maid = models.OneToOneField(
#         Maid,
#         on_delete=models.CASCADE,
#         related_name='other_care'
#     )

#     care_for_pets = models.BooleanField(
#         verbose_name=_('Care for pets'),
#         blank=False,
#         choices=TrueFalseChoices('Able', 'Unable'),
#         default=False
#     )

#     gardening = models.BooleanField(
#         verbose_name=_('Gardening'),
#         blank=False,
#         choices=TrueFalseChoices('Able', 'Unable'),
#         default=False
#     )
    