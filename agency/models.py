# Imports from python

# Imports from django
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import ugettext_lazy as _

# Imports from other apps
from onlinemaid.helper_functions import get_sg_region
from onlinemaid.storage_backends import PublicMediaStorage

# Imports from within the app
from .constants import (
    AreaChoices, AgencyEmployeeRoleChoices, OpeningHoursChoices
)
from .validators import validate_postcode

# Utiliy Classes and Functions

# Start of Models

class Agency(models.Model):
    name = models.CharField(
        verbose_name=_('Company Name'),
        max_length=100,
        blank=False
    )

    license_number = models.CharField(
        verbose_name=_('License number'),
        max_length=100,
        blank=False
    )

    website_uri = models.CharField(
        verbose_name=_('Website URL'),
        max_length=100,
        blank=True,
        null=True,
        validators=[
            URLValidator(
                message=_('Please enter a valid URL')
            )
        ]   
    )

    logo = models.FileField(
        verbose_name=_('Website Logo'),
        blank=True,
        null=True,
        storage=PublicMediaStorage() if settings.USE_S3 else None
    )

    profile = models.TextField(
        verbose_name=_('Profile'),
        blank=False
    )
    
    services = models.TextField(
        verbose_name=_('Services'),
        blank=False
    )
    
    amount_of_biodata = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of FDW Biodata'),
        default=0,
        null=False
    )
    
    amount_of_biodata_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of FDW Biodata allowed'),
        default=0,
        null=False
    )
    
    amount_of_featured_biodata = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of featured FDW Biodata'),
        default=0,
        null=False
    )
    
    amount_of_featured_biodata_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of featured FDW Biodata allowed'),
        default=0,
        null=False
    )
    
    amount_of_employees = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employee accounts'),
        default=0,
        null=False
    )
    
    amount_of_employees_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employee accounts allowed'),
        default=0,
        null=False
    )
    
    amount_of_documents = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employer documents'),
        default=0,
        null=False
    )
    
    amount_of_documents_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employer documents allowed'),
        default=0,
        null=False
    )

    active = models.BooleanField(
        default=True,
        editable=False
    )

    def __str__(self):
        return self.name

    def get_main_office_number(self):
        return self.branches.get(main_branch=True).office_number

    def get_main_office(self):
        return self.branches.get(main_branch=True)
    
    def get_enquiries(self):
        return self.enquiries.all()
    
    def get_biodata_limit_status(self):
        return (
            self.amount_of_biodata < self.amount_of_biodata_allowed and
            self.amount_of_biodata_allowed != 0
        )

    class Meta:
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'
        
# Models which are one to one with Agency
class AgencyOpeningHours(models.Model):
    agency = models.OneToOneField(
        Agency,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='opening_hours'
    )

    type = models.CharField(
        verbose_name=_('Agency\'s operating hours type'),
        max_length=2,
        blank=False,
        choices=OpeningHoursChoices.choices,
        default=OpeningHoursChoices.OPENING_HOURS
    )

    monday = models.CharField(
        verbose_name=_('Monday\'s opening hours'),
        max_length=30,
        blank=True
    )

    tuesday = models.CharField(
        verbose_name=_('Tuesday\'s opening hours'),
        max_length=30,
        blank=True
    )

    wednesday = models.CharField(
        verbose_name=_('Wednesday\'s opening hours'),
        max_length=30,
        blank=True
    )

    thursday = models.CharField(
        verbose_name=_('Thursday\'s opening hours'),
        max_length=30,
        blank=True
    )

    friday = models.CharField(
        verbose_name=_('Friday\'s opening hours'),
        max_length=30,
        blank=True
    )

    saturday = models.CharField(
        verbose_name=_('Saturday\'s opening hours'),
        max_length=30,
        blank=True
    )

    sunday = models.CharField(
        verbose_name=_('Sunday\'s opening hours'),
        max_length=30,
        blank=True
    )

    public_holiday = models.CharField(
        verbose_name=_('Public holiday opening hours'),
        max_length=30,
        blank=True
    )


    def __str__(self):
        return f'Operating Hours for {self.agency.name}'

    class Meta:
        verbose_name = 'Agency Operating Hour'
        verbose_name_plural = 'Agency Operating Hours'

# Models which are many to one with Agency
class AgencyOwner(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='agency_owner'
    )

    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='owners'
    )

    def __str__(self):
        return self.agency.name + ' Owner'

    class Meta:
        verbose_name = 'Agency Owner'
        verbose_name_plural = 'Agency Owners'

class AgencyBranch(models.Model):
    MAIN_BRANCH_CHOICES = (
        (True, _('Yes')),
        (False, _('No'))
    )

    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='branches'
    )

    name = models.CharField(
        verbose_name=_('Branch Name'),
        max_length=50,
        blank=False,
        null=True
    )

    address_1 = models.CharField(
        verbose_name=_('Street Address'),
        max_length=100,
        blank=False,
        null=True
    )

    address_2 = models.CharField(
        verbose_name=_('Unit Number'),
        max_length=50,
        blank=False,
        null=True
    )

    postal_code = models.CharField(
        verbose_name=_('Postal Code'),
        max_length=25,
        blank=False,
        null=True,
        validators=[validate_postcode],
    )

    area = models.CharField(
        verbose_name=_('Area'),
        max_length=2,
        editable=False,
        blank=False,
        choices=AreaChoices.choices,
        default=AreaChoices.CENTRAL
    )

    office_number = models.CharField(
        verbose_name=_('Office Number'),
        max_length=10,
        blank=False,
        null=True,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid contact number')
            )
        ]
        # This regex validator checks if the contact number provided is all 
        # numbers.
    )

    mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=10,
        blank=False,
        null=True,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid contact number')
            )
        ]
        # This regex validator checks if the contact number provided is all 
        # numbers.
    )

    main_branch = models.BooleanField(
        verbose_name=_('Main Branch'),
        choices=MAIN_BRANCH_CHOICES,
        default=True
    )
    
    email = models.EmailField(
        verbose_name=_('Branch Email Address'),
        blank=False
    )

    def __str__(self):
        return self.agency.name + ', ' + self.name if self.name else self.agency.name + ' branch'

    def save(self, *args, **kwargs):
        sg_region = get_sg_region(self.postal_code)
        if not sg_region:
            sg_region = AreaChoices.choices[0][0]
        self.area = sg_region
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Agency Branch'
        verbose_name_plural = 'Agency Branches'

class AgencyPlan(models.Model):
    class PlanTypeChoices(models.TextChoices):
        BIODATA_100 = 'B100', _('100 Biodata')
        BIODATA_200 = 'B200', _('200 Biodata')
        BIODATA_300 = 'B300', _('300 Biodata')
        
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE
    )

    choice = models.CharField(
        verbose_name=_('Plan type'),
        max_length=4,
        blank=False,
        choices=PlanTypeChoices.choices,
        default=PlanTypeChoices.BIODATA_100
    )

    expiry_date = models.DateTimeField(
        verbose_name=_('Plan expiry date'),
        editable=False
    )

    remarks = models.CharField(
        verbose_name=_('Remarks'),
        max_length=100,
        blank=True
    )

# Agency Employee Models
class AgencyEmployee(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='agency_employee'
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        blank=False
    )

    contact_number = models.CharField(
        verbose_name=_('Contact Number'),
        max_length=50,
        blank=False,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid contact number')
            )
        ]
        # This regex validator checks if the contact number provided is all 
        # numbers.
    )

    ea_personnel_number = models.CharField(
        verbose_name=_('EA personnel number'),
        max_length=50,
        blank=False
    )

    email = models.EmailField(
        verbose_name=_('Employee\'s Email Address'),
        null=True,
        blank=True,
        help_text=_('Optional')
    )

    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    branch = models.ForeignKey(
        AgencyBranch,
        on_delete=models.CASCADE,
        related_name='employees'
    )

    role = models.CharField(
        verbose_name=_('Employee Role'),
        max_length=2,
        blank=False,
        choices=AgencyEmployeeRoleChoices.choices,
        default=AgencyEmployeeRoleChoices.SALES_STAFF
    )

    deleted = models.BooleanField(
        editable=False,
        default=False
    )

    published = models.BooleanField(
        editable=False,
        default=False
    )
    
    def __str__(self):
        return self.ea_personnel_number + ' - ' + self.name

    def get_ea_personnel_no(self):
        return self.ea_personnel_number
    
    class Meta:
        verbose_name = 'Agency Employee'
        verbose_name_plural = 'Agency Employees'

class PotentialAgency(models.Model):
    name = models.CharField(
        verbose_name=_('Agency Name'),
        max_length=100,
        blank=False
    )

    license_number = models.CharField(
        verbose_name=_('License number'),
        max_length=100,
        blank=False
    )

    person_in_charge = models.CharField(
        verbose_name=_('Person In Charge'),
        max_length=100,
        blank=False
    )

    contact_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=8,
        blank=False,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid mobile number')
            )
        ]
        # This regex validator checks if the contact number provided is all 
        # numbers.
    )

    office_number = models.CharField(
        verbose_name=_('Office Number'),
        max_length=8,
        blank=False,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid office number')
            )
        ]
        # This regex validator checks if the office number provided is all 
        # numbers.
    )

    email = models.EmailField(
        verbose_name=_('Email Address'),
        blank=False
    )