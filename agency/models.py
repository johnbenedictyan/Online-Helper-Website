import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from onlinemaid.fields import NullableCharField
from onlinemaid.helper_functions import get_sg_region
from onlinemaid.storage_backends import PublicMediaStorage
from onlinemaid.validators import validate_ea_personnel_number

from .constants import (AgencyEmployeeRoleChoices, AreaChoices,
                        OpeningHoursTypeChoices)
from .fields import OpeningHoursField
from .validators import validate_postcode

# Utiliy Classes and Functions

# Start of Models


class Agency(models.Model):
    name = models.CharField(
        verbose_name=_('Company Name'),
        max_length=100
    )

    license_number = models.CharField(
        verbose_name=_('License number'),
        max_length=100
    )

    website_uri = NullableCharField(
        verbose_name=_('Website URL'),
        max_length=100,
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
        verbose_name=_('Profile')
    )

    services = models.TextField(
        verbose_name=_('Services')
    )

    amount_of_biodata = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of FDW Biodata'),
        default=0
    )

    amount_of_biodata_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of FDW Biodata allowed'),
        default=0
    )

    amount_of_featured_biodata = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of featured FDW Biodata'),
        default=0
    )

    amount_of_featured_biodata_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of featured FDW Biodata allowed'),
        default=0
    )

    amount_of_employees = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employee accounts'),
        default=0
    )

    amount_of_employees_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employee accounts allowed'),
        default=0
    )

    amount_of_documents = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employer documents'),
        default=0
    )

    amount_of_documents_allowed = models.PositiveSmallIntegerField(
        verbose_name=_('Amount of employer documents allowed'),
        default=0
    )

    active = models.BooleanField(
        default=True,
        editable=False
    )

    name_url = NullableCharField(
        max_length=255
    )

    __original_branch_address_line_1 = None
    __original_branch_address_line_2 = None
    __original_branch_postal_code = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_branch = self.get_main_branch()
        if main_branch:
            self.__original_branch_address_line_1 = main_branch.address_1
            self.__original_branch_address_line_2 = main_branch.address_2
            self.__original_branch_postal_code = main_branch.postal_code

    def __str__(self) -> str:
        return self.name

    def get_main_branch(self):
        main_branches_qs = self.branches.filter(main_branch=True)
        if main_branches_qs.count():
            return main_branches_qs[0]
        else:
            return None

    def get_main_branch_number(self):
        main_branch = self.get_main_branch()
        if main_branch:
            return main_branch.office_number
        else:
            return None

    def get_branches(self):
        return self.branches.filter(main_branch=False)

    def get_biodata_limit_status(self):
        return (
            self.amount_of_biodata < self.amount_of_biodata_allowed
            and self.amount_of_biodata_allowed != 0
        )

    def get_agency_owner_email(self):
        return self.agency_owner.user.email

    def get_number_of_featured_fdw(self):
        return self.amount_of_featured_biodata

    def get_number_of_unpublished_fdw(self):
        return len(
            list(maid for maid in self.maid.all() if not maid.is_published)
        )

    def get_number_of_published_fdw(self):
        return len(
            list(maid for maid in self.maid.all() if maid.is_published)
        )

    def create_or_update_stripe_customer(self):
        from payment.models import Customer

        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not self.has_customer_relation():
            stripe_customer = stripe.Customer.create(
                address={
                    'city': 'Singapore',
                    'country': 'Singapore',
                    'line1': self.get_main_branch().address_1,
                    'line2': self.get_main_branch().address_2,
                    'postal_code': self.get_main_branch().postal_code,
                    'state': 'Singapore',
                },
                description=f'Customer account for {self.name}',
                email=self.get_agency_owner_email(),
                name=self.name
            )
            new_customer = Customer.objects.create(
                id=stripe_customer['id'],
                agency=self
            )
            new_customer.save()
            return new_customer
        else:
            stripe_customer_pk = self.customer_account
            stripe.Customer.modify(
                stripe_customer_pk,
                email=self.get_agency_owner_email()
            )

    def has_customer_relation(self):
        return hasattr(self, 'customer_account')

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
        choices=OpeningHoursTypeChoices.choices,
        default=OpeningHoursTypeChoices.OPENING_HOURS
    )

    monday_start = OpeningHoursField(
        verbose_name=_('Monday\'s opening time')
    )

    monday_end = OpeningHoursField(
        verbose_name=_('Monday\'s closing time')
    )

    monday_closed = models.BooleanField(
        verbose_name=_('Monday opening status'),
        default=False
    )

    tuesday_start = OpeningHoursField(
        verbose_name=_('Tuesday\'s opening time')
    )

    tuesday_end = OpeningHoursField(
        verbose_name=_('Tuesday\'s closing time')
    )

    tuesday_closed = models.BooleanField(
        verbose_name=_('Tuesday opening status'),
        default=False
    )

    wednesday_start = OpeningHoursField(
        verbose_name=_('Wednesday\'s opening time')
    )

    wednesday_end = OpeningHoursField(
        verbose_name=_('Wednesday\'s closing time')
    )

    wednesday_closed = models.BooleanField(
        verbose_name=_('Wednesday opening status'),
        default=False
    )

    thursday_start = OpeningHoursField(
        verbose_name=_('Thursday\'s opening time')
    )

    thursday_end = OpeningHoursField(
        verbose_name=_('Thursday\'s closing time')
    )

    thursday_closed = models.BooleanField(
        verbose_name=_('Thursday opening status'),
        default=False
    )

    friday_start = OpeningHoursField(
        verbose_name=_('Friday\'s opening time')
    )

    friday_end = OpeningHoursField(
        verbose_name=_('Friday\'s closing time')
    )

    friday_closed = models.BooleanField(
        verbose_name=_('Friday opening status'),
        default=False
    )

    saturday_start = OpeningHoursField(
        verbose_name=_('Saturday\'s opening time')
    )

    saturday_end = OpeningHoursField(
        verbose_name=_('Saturday\'s closing time')
    )

    saturday_closed = models.BooleanField(
        verbose_name=_('Saturday opening status'),
        default=False
    )

    sunday_start = OpeningHoursField(
        verbose_name=_('Sunday\'s opening time')
    )

    sunday_end = OpeningHoursField(
        verbose_name=_('Sunday\'s closing time')
    )

    sunday_closed = models.BooleanField(
        verbose_name=_('Sunday opening status'),
        default=False
    )

    public_holiday_start = OpeningHoursField(
        verbose_name=_('Public holiday opening time')
    )

    public_holiday_end = OpeningHoursField(
        verbose_name=_('Public holiday closing time')
    )

    public_holiday_closed = models.BooleanField(
        verbose_name=_('Public Holiday opening status'),
        default=False
    )

    def __str__(self) -> str:
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

    agency = models.OneToOneField(
        Agency,
        on_delete=models.CASCADE,
        related_name='agency_owner'
    )

    name = models.CharField(
        verbose_name=_('Agency Owner Name'),
        max_length=50
    )

    mobile_number = models.CharField(
        verbose_name=_('Agency Owner Mobile Number'),
        max_length=50,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid contact number')
            )
        ]
    )

    test_email = models.BooleanField(
        default=True,
        editable=False
    )

    def __str__(self) -> str:
        return self.agency.name + ' Owner'

    def is_test_email(self):
        return self.test_email

    def unset_test_email(self):
        self.test_email = False
        self.save()

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
        max_length=50
    )

    address_1 = models.CharField(
        verbose_name=_('Street Address'),
        max_length=100
    )

    address_2 = models.CharField(
        verbose_name=_('Unit Number'),
        max_length=50
    )

    postal_code = models.CharField(
        verbose_name=_('Postal Code'),
        max_length=25,
        validators=[validate_postcode]
    )

    area = models.CharField(
        verbose_name=_('Area'),
        max_length=2,
        editable=False,
        choices=AreaChoices.choices,
        default=AreaChoices.CENTRAL
    )

    office_number = models.CharField(
        verbose_name=_('Office Number'),
        max_length=10,
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
        verbose_name=_('Branch Email Address')
    )

    def __str__(self) -> str:
        if self.name:
            return self.agency.name + ', ' + self.name
        else:
            return self.agency.name + ' branch'

    def save(self, *args, **kwargs):
        sg_region = get_sg_region(self.postal_code)
        self.area = sg_region if sg_region else AreaChoices.choices[0][0]
        super().save(*args, **kwargs)

    def get_employees(self):
        return self.employees.filter(branch=self)

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
        choices=PlanTypeChoices.choices,
        default=PlanTypeChoices.BIODATA_100
    )

    expiry_date = models.DateTimeField(
        verbose_name=_('Plan expiry date'),
        editable=False
    )

    remarks = NullableCharField(
        verbose_name=_('Remarks'),
        max_length=100
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
        max_length=255
    )

    contact_number = models.CharField(
        verbose_name=_('Contact Number'),
        max_length=50,
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
        default='NA',
        blank=True,
        help_text=_('Optional for non-personnel')
    )

    email = models.EmailField(
        verbose_name=_('Employee\'s Email Address')
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

    def __str__(self) -> str:
        return self.ea_personnel_number + ' - ' + self.name

    def get_ea_personnel_no(self):
        return self.ea_personnel_number

    def is_ea_personnel_no_valid(self):
        if validate_ea_personnel_number(self.ea_personnel_number):
            return False
        else:
            return True

    def get_all_ea_personnel_no_in_branch(self):
        if self.role == AgencyEmployeeRoleChoices.MANAGER:
            return list(
                AgencyEmployee.objects.filter(
                    branch=self.branch
                ).values_list(
                    'ea_personnel_number',
                    flat=True
                )
            )

    class Meta:
        verbose_name = 'Agency Employee'
        verbose_name_plural = 'Agency Employees'


class PotentialAgency(models.Model):
    name = models.CharField(
        verbose_name=_('Agency Name'),
        max_length=100
    )

    license_number = models.CharField(
        verbose_name=_('License number'),
        max_length=100
    )

    person_in_charge = models.CharField(
        verbose_name=_('Person In Charge'),
        max_length=100
    )

    contact_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=8,
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
        verbose_name=_('Email Address')
    )
