# Imports from python

# Imports from django
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, URLValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

# Imports from other apps

# Imports from within the app

# Utiliy Classes and Functions

# Start of Models

class Agency(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True
    )

    company_email = models.EmailField(
        blank=False
    )

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
        blank=False,
        validators=[
            URLValidator(
                message=_('Please enter a valid URL')
            )
        ]   
    )

    logo_uri = None

    uen = models.CharField(
        verbose_name=_('Company\'s UEN code'),
        max_length=10,
        blank=False
    )

    qr_code = None

    active = models.BooleanField(
        default=True,
        editable=False
    )

    complete = models.BooleanField(
        default=False,
        editable=False
    )

    location_complete = models.BooleanField(
        default=False,
        editable=False
    )

    contact_information_complete = models.BooleanField(
        default=False,
        editable=False
    )

    operating_hours_complete = models.BooleanField(
        default=False,
        editable=False
    )

class AgencyEmployee(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True
    )

    first_name = models.CharField(
        verbose_name=_('First Name'),
        max_length=50,
        blank=False
    )

    last_name = models.CharField(
        verbose_name=_('Last Name'),
        max_length=50,
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

    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name='employees'
    )

# Models which are one to one field with Agency
class AgencyLocation(models.Model):
    class AreaChoices(models.TextChoices):
        CENTRAL = 'C', _('Central')
        NORTH = 'N', _('North')
        NORTH_EAST = 'NE', _('North East')
        EAST = 'E', _('East')
        WEST = 'W', _('West')

    agency = models.OneToOneField(
        Agency,
        on_delete=models.CASCADE,
        primary_key=True
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
        null=True
    )

    area = models.CharField(
        verbose_name=_('Area'),
        max_length=2,
        blank=False,
        choices=AreaChoices.choices,
        default=AreaChoices.CENTRAL
    )
    
class AgencyContactInformation(models.Model):
    agency = models.OneToOneField(
        Agency,
        on_delete=models.CASCADE,
        primary_key=True
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

    sales_email = models.EmailField(
        blank=False,
        null=True
    )

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

class AgencyOperatingHours(models.Model):
    class OperatingHoursChoices(models.TextChoices):
        OPENING_HOURS = 'OH', _('Opening Hours')
        APPOINTMENT_ONLY = 'AO', _('Appointment Only')

    agency = models.OneToOneField(
        Agency,
        on_delete=models.CASCADE,
        primary_key=True
    )

    operating_type = models.CharField(
        verbose_name=_('Agency\'s operating hours type'),
        max_length=2,
        blank=False,
        choices=OperatingHoursChoices.choices,
        default=OperatingHoursChoices.OPENING_HOURS
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

# Django Signals
@receiver(post_save, sender=AgencyLocation)
@receiver(post_save, sender=AgencyContactInformation)
@receiver(post_save, sender=AgencyOperatingHours)
def agency_completed(sender, instance, **kwargs):
    agency = instance.agency
    if(
        agency.location_complete == True and 
        agency.contact_information_complete == True and 
        agency.location_complete == True
    ):
        agency.completed = True
        agency.save()

@receiver(post_save, sender=AgencyLocation)
def agency_location_completed(sender, instance, created, **kwargs):
    if created == False:
        agency = instance.agency
        location_valid = True

        while location_valid == True:
            for i in sender.values():
                if not i:
                    location_valid = False
        
        agency.location_complete = location_valid
        agency.save()

@receiver(post_save, sender=AgencyContactInformation)
def agency_contact_information_completed(sender, instance, created, **kwargs):
    if created == False:
        agency = instance.agency
        contact_information_valid = True
        
        while contact_information_valid == True:
            for i in sender.values():
                if not i:
                    contact_information_valid = False
        
        agency.contact_information_complete = contact_information_valid
        agency.save()

@receiver(post_save, sender=AgencyOperatingHours)
def agency_operating_hours_completed(sender, instance, created, **kwargs):
    if created == False:
        agency = instance.agency
        operating_hours_valid = True
        
        while operating_hours_valid == True:
            for i in sender.values():
                if not i:
                    operating_hours_valid = False
        
        agency.operating_hours_complete = operating_hours_valid
        agency.save()

@receiver(post_save, sender=Agency)
def new_agency_created(sender, instance, created, **kwargs):
    if created == True:
        agency = instance
        AgencyContactInformation.objects.create(
            agency=agency
        )
        AgencyLocation.objects.create(
            agency=agency
        )
        AgencyOperatingHours.objects.create(
            agency=agency
        )