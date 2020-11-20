# Imports from python

# Imports from django
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

# Imports from within the app
from .managers import CustomUserManager

# Utiliy Classes and Functions

# Start of Models

# User Models
class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        EMPLOYER = 'E', _('Employer')
        AGENCY_OWNER = 'AO', _('Agency Owner')
        AGENCY_ADMINISTRATOR = 'AA', _('Agency Administrator')
        AGENCY_MANAGER = 'AM', _('Agency Manager')
        AGENCY_SALESSTAFF = 'AE', _('Agency Sales Staff')

    username = None
    first_name = None
    last_name = None
    email = models.EmailField(
        _('Email Address'), 
        unique=True
    )
    role = models.CharField(
        verbose_name=_('Role'),
        max_length=2,
        choices=RoleChoices.choices,
        default=RoleChoices.EMPLOYER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'

class Employer(models.Model):
    user = models.OneToOneField(
        User,
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
        max_length=10,
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
