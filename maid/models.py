# Imports from python

# Imports from django
from django.db import models
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

# Imports from project
from onlinemaid.constants import TrueFalseChoices
from onlinemaid.storage_backends import PublicMediaStorage, PrivateMediaStorage

# Imports from other apps
from agency.models import Agency

# Imports from within the app
from .constants import (
    TypeOfMaidChoices, MaidCountryOfOrigin, MaidAssessmentChoices, 
    MaidCareRemarkChoices, MaidLanguageChoices, MaidResponsibilityChoices,
    MaritalStatusChoices
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
    class PassportStatusChoices(models.IntegerChoices):
        NOT_READY = 0, _('Not Ready')
        READY = 1, _('Ready')
        
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

    passport_number = models.BinaryField(editable=True)
    nonce = models.BinaryField(editable=True)
    tag = models.BinaryField(editable=True)

    photo = models.FileField(
        verbose_name=_('Maid Photo'),
        blank=False,
        null=True,
        # storage=PublicMediaStorage()
    )

    maid_type = models.CharField(
        verbose_name=_('Maid Type'),
        max_length=3,
        blank=False,
        choices=TypeOfMaidChoices.choices,
        default=TypeOfMaidChoices.NEW
    )

    salary = models.DecimalField(
        verbose_name=_('Salary'),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        blank=False,
        default=0
    )

    agency_fee_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        editable=False,
        default=0
    )

    personal_loan_amount = models.DecimalField(
        verbose_name=_('Personal loan amount'),
        max_digits=7,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000),
        ],
        blank=False,
        default=0
    )

    days_off = models.PositiveSmallIntegerField(
        verbose_name=_('Days off'),
        blank=False,
        default=0
    )

    passport_status = models.BooleanField(
        verbose_name=_('Passport status'),
        max_length=1,
        blank=False,
        choices=PassportStatusChoices.choices,
        default=PassportStatusChoices.NOT_READY
    )

    repatriation_airport = models.CharField(
        verbose_name=_('Repatriation airport'),
        max_length=100,
        blank=False
    )

    remarks = models.CharField(
        verbose_name=_('Remarks'),
        max_length=255,
        blank=False
    )
    
    responsibilities = models.ManyToManyField(
        MaidResponsibility
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

    complete = models.BooleanField(
        default=False,
        blank=True,
        editable=False
    )

    biodata_complete = models.BooleanField(
        default=False,
        blank=True,
        editable=False
    )

    family_details_complete = models.BooleanField(
        default=False,
        blank=True,
        editable=False
    )

    care_complete = models.BooleanField(
        default=False,
        blank=True,
        editable=False
    )

    published = models.BooleanField(
        default=False,
        blank=False
    )

    featured = models.BooleanField(
        default=False,
        blank=False
    )

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

class MaidEmploymentHistory(models.Model):
    class MaidEmploymentCounty(models.TextChoices):
        SINGAPORE = 'SG', _('SINGAPORE')

    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='employment_history'
    )

    start_date = models.DateTimeField(
        verbose_name="Maid employment's start date"
    )

    end_date = models.DateTimeField(
        verbose_name="Maid employment's end date"
    )

    country = models.CharField(
        verbose_name=_("Country of employment"),
        max_length=3,
        blank=False,
        choices=MaidEmploymentCounty.choices
    )

    work_duration = models.DurationField(
        verbose_name=_('Employment duration'),
        blank=True,
        editable=False
    )

    work_duties = models.ManyToManyField(
        MaidWorkDuty
    )

    def save(self, *args, **kwargs):
        self.work_duration = self.end_date - self.start_date
        super().save(self, *args, **kwargs)

class MaidAgencyFeeTransaction(models.Model):
    TRANSCATION_CHOICES = (
        ('ADD', _('Loan Increase')),
        ('SUB', _('Loan Repayment'))
    )

    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='agency_fee_transactions'
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

    transaction_type = models.CharField(
        verbose_name=_("Type of transaction"),
        max_length=3,
        blank=False,
        choices=TRANSCATION_CHOICES
    )

    description = models.TextField(
        verbose_name=_('Description of transaction'),
        blank=False
    )

## Models which have a one-to-one relationship with the maid model 
class MaidBiodata(models.Model):
    class ReligionChoices(models.TextChoices):
        BUDDHIST = 'B', _('Buddhist')
        MUSLIM = 'M', _('Muslim')
        HINDU = 'H', _('Hindu')
        CHRISTIAN = 'CH', _('Christain')
        CATHOLIC = 'CA', _('Catholic')
        SIKH = 'S', _('Sikh')
        OTHERS = 'OTH', _('Others')
        NONE = 'NONE', _('None')

    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='biodata'
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=False,
        null=True
    )

    age = models.IntegerField(
        verbose_name=_('Age'),
        blank=False,
        null=True
    )

    country_of_origin = models.CharField(
        verbose_name=_('Country of Origin'),
        max_length=3,
        blank=False,
        null=True,
        choices=MaidCountryOfOrigin.choices
    )

    height = models.PositiveSmallIntegerField(
        verbose_name=_('Height (in cm)'),
        blank=False,
        null=True
    )

    weight = models.PositiveSmallIntegerField(
        verbose_name=_('Weight (in kg)'),
        blank=False,
        null=True
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

    religion = models.CharField(
        verbose_name=_('Religion'),
        max_length=4,
        blank=False,
        choices=ReligionChoices.choices,
        default=ReligionChoices.NONE
    )

    languages = models.ManyToManyField(
        MaidLanguage
    )

class MaidStatus(models.Model):
    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='status'
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

class MaidFamilyDetails(models.Model):
    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='family_details'
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

class MaidOtherCare(models.Model):
    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='other_care'
    )

    care_for_pets = models.BooleanField(
        verbose_name=_('Care for pets'),
        blank=False,
        default=False
    )

    gardening = models.BooleanField(
        verbose_name=_('Gardening'),
        blank=False,
        default=False
    )