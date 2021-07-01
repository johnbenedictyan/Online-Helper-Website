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
from onlinemaid.helper_functions import decrypt_string, humanise_time_duration
from onlinemaid.storage_backends import PublicMediaStorage

# Imports from other apps
from agency.models import Agency

# Imports from within the app
from .constants import (
    TypeOfMaidChoices, MaidAssessmentChoices, MaidPassportStatusChoices, MaidLanguageChoices, 
    MaidResponsibilityChoices, MaritalStatusChoices, MaidReligionChoices, MaidEducationLevelChoices,
    MaidLoanDescriptionChoices, MaidStatusChoices, MaidFoodPreferenceChoices, 
    MaidDietaryRestrictionChoices, MaidNationalityChoices, MaidLanguageProficiencyChoices,
    MaidExperienceChoices, MaidEmploymentCountry, InfantChildCareRemarksChoices, 
    ElderlyCareRemarksChoices, DisabledCareRemarksChoices, GeneralHouseworkRemarksChoices,
    CookingRemarksChoices
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
        editable=True,
        blank=True,
        null=True
    )
    
    passport_number_nonce = models.BinaryField(
        editable=True,
        blank=True
    )
    
    passport_number_tag = models.BinaryField(
        editable=True,
        blank=True
    )

    photo = models.FileField(
        verbose_name=_('Maid Photo'),
        blank=False,
        null=True,
        storage=PublicMediaStorage() if settings.USE_S3 else None
    )

    maid_type = models.CharField(
        verbose_name=_('Maid Type'),
        max_length=6,
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
        null=True,
        blank=True
    )
    
    languages = models.ManyToManyField(
        MaidLanguage
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

    status = models.CharField(
        verbose_name=_('Status'),
        max_length=6,
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
        verbose_name=_('Nationality'),
        max_length=3,
        blank=False,
        null=True,
        choices=MaidNationalityChoices.choices
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
        blank=True,
        null=True,
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
    
    about_me = models.TextField(
        verbose_name=_('About Me'),
        max_length=350,
        null=True
    )
    
    fin_number = models.BinaryField(
        verbose_name=_('FDW FIN'),
        editable=True,
        blank=True,
        null=True
    )

    fin_number_nonce = models.BinaryField(
        editable=True,
        blank=True,
        null=True
    )

    fin_number_tag = models.BinaryField(
        editable=True,
        blank=True,
        null=True
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
            self.passport_number_nonce,
            self.passport_number_tag
        )
        return plaintext

    def get_fin_number(self):
        plaintext = decrypt_string(
            self.fin_number,
            settings.ENCRYPTION_KEY,
            self.fin_number_nonce,
            self.fin_number_tag
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

    def get_fdw_fin_full(self):
        return decrypt_string(
            self.fin_number,
            settings.ENCRYPTION_KEY,
            self.fin_number_nonce,
            self.fin_number_tag
        )
    
    def get_fdw_fin_partial(self, padded=True):
        plaintext = self.get_fdw_fin_full()
        if padded == True:
            return 'x'*5 + plaintext[-4:] if plaintext else ''
        else:
            return plaintext[-4:] if plaintext else ''

    def toggle_published(self):
        if self.status == MaidStatusChoices.PUBLISHED:
            self.status = MaidStatusChoices.UNPUBLISHED
        elif self.status == MaidStatusChoices.UNPUBLISHED:
            self.status = MaidStatusChoices.PUBLISHED
        elif self.status == MaidStatusChoices.FEATURED:
            self.status = MaidStatusChoices.UNPUBLISHED
        self.save()
    
    def toggle_featured(self):
        err_msg = None
        amt_of_featured = self.agency.amount_of_featured_biodata
        amt_allowed = self.agency.amount_of_featured_biodata_allowed    
        if self.status == MaidStatusChoices.PUBLISHED:
            if amt_of_featured < amt_allowed:
                self.status = MaidStatusChoices.FEATURED
            else:
                err_msg = 'You have reached the limit of featured biodata'
        elif self.status == MaidStatusChoices.FEATURED:
            self.status = MaidStatusChoices.PUBLISHED
        self.save()
        return err_msg
            
    @property
    def is_published(self):
        return (
            self.status == MaidStatusChoices.PUBLISHED or self.status == MaidStatusChoices.FEATURED
        )
    
    @property
    def is_featured(self):
        return self.status == MaidStatusChoices.FEATURED

## Models which have a one-to-many relationship with the maid model
class MaidFoodHandlingPreference(models.Model):
    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='food_handling_preferences'
    )

    preference = models.CharField(
        verbose_name = _('Food preference'),
        max_length=1,
        blank=False,
        choices=MaidFoodPreferenceChoices.choices,
        default=MaidFoodPreferenceChoices.PORK
    )

class MaidDietaryRestriction(models.Model):
    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='dietary_restrictions'
    )

    restriction = models.CharField(
        verbose_name = _('Dietary restriction'),
        max_length=1,
        blank=False,
        choices=MaidDietaryRestrictionChoices.choices,
        default=MaidDietaryRestrictionChoices.PORK
    )

class MaidEmploymentHistory(models.Model):
    maid = models.ForeignKey(
        Maid,
        on_delete=models.CASCADE,
        related_name='employment_history'
    )

    start_date = models.DateField(
        verbose_name="Past employment's start date"
    )

    end_date = models.DateField(
        verbose_name="Past employment's end date"
    )

    country = models.CharField(
        verbose_name=_("Country of employment"),
        max_length=3,
        blank=False,
        choices=MaidEmploymentCountry.choices,
        default=MaidEmploymentCountry.SINGAPORE
    )

    race_of_employer = models.CharField(
        verbose_name=_('Race of employer'),
        max_length=255,
        blank=False
    )

    work_duties = models.CharField(
        verbose_name=_('Work Duties'),
        max_length=150,
        blank=False
    )

    reason_for_leaving = models.CharField(
        verbose_name=_('Reason for leaving'),
        max_length=100,
        blank=False
    )

    def work_duration(self):
        duration = self.end_date - self.start_date
        return humanise_time_duration(duration)

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
class MaidInfantChildCare(models.Model):
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
        verbose_name=_('Willingness'),
        blank=False,
        choices=TrueFalseChoices('Yes', 'No'),
        default=True,
    )

    experience = models.CharField(
        verbose_name=_('Experience with infant child care'),
        blank=False,
        max_length=6,
        choices=MaidExperienceChoices.choices,
        default=MaidExperienceChoices.NO
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
        verbose_name=_('Willingness'),
        blank=False,
        choices=TrueFalseChoices('Yes', 'No'),
        default=True,
    )

    experience = models.CharField(
        verbose_name=_('Experience with elderly care'),
        blank=False,
        max_length=6,
        choices=MaidExperienceChoices.choices,
        default=MaidExperienceChoices.NO
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
        verbose_name=_('Willingness'),
        blank=False,
        choices=TrueFalseChoices('Yes', 'No'),
        default=True,
    )

    experience = models.CharField(
        verbose_name=_('Experience with disabled care'),
        blank=False,
        max_length=6,
        choices=MaidExperienceChoices.choices,
        default=MaidExperienceChoices.NO
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
        verbose_name=_('Willingness'),
        blank=False,
        choices=TrueFalseChoices('Yes', 'No'),
        default=True,
    )

    experience = models.CharField(
        verbose_name=_('Experience with general housework'),
        blank=False,
        max_length=6,
        choices=MaidExperienceChoices.choices,
        default=MaidExperienceChoices.NO
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
        verbose_name=_('Willingness'),
        blank=False,
        choices=TrueFalseChoices('Yes', 'No'),
        default=True,
    )

    experience = models.CharField(
        verbose_name=_('Experience with cooking'),
        blank=False,
        max_length=6,
        choices=MaidExperienceChoices.choices,
        default=MaidExperienceChoices.NO
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

class MaidLanguageProficiency(models.Model):
    maid = models.OneToOneField(
        Maid,
        on_delete=models.CASCADE,
        related_name='language_proficiency'
    )
    
    english = models.CharField(
        verbose_name=_('English'),
        blank=False,
        max_length=6,
        choices=MaidLanguageProficiencyChoices.choices,
        default=MaidLanguageProficiencyChoices.UNABLE
    )
    
    malay = models.CharField(
        verbose_name=_('Malay / Bahasa Indonesia'),
        blank=False,
        max_length=6,
        choices=MaidLanguageProficiencyChoices.choices,
        default=MaidLanguageProficiencyChoices.UNABLE
    )
    
    mandarin = models.CharField(
        verbose_name=_('Mandarin'),
        blank=False,
        max_length=6,
        choices=MaidLanguageProficiencyChoices.choices,
        default=MaidLanguageProficiencyChoices.UNABLE
    )
    
    chinese_dialect = models.CharField(
        verbose_name=_('Chinese Dialect'),
        blank=False,
        max_length=6,
        choices=MaidLanguageProficiencyChoices.choices,
        default=MaidLanguageProficiencyChoices.UNABLE
    )
    
    hindi = models.CharField(
        verbose_name=_('Hindi'),
        blank=False,
        max_length=6,
        choices=MaidLanguageProficiencyChoices.choices,
        default=MaidLanguageProficiencyChoices.UNABLE
    )
    
    tamil = models.CharField(
        verbose_name=_('Tamil'),
        blank=False,
        max_length=6,
        choices=MaidLanguageProficiencyChoices.choices,
        default=MaidLanguageProficiencyChoices.UNABLE
    )
