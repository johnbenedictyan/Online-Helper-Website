# Imports from python

# Imports from django
from django.db import models
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.utils.translation import ugettext_lazy as _

# Imports from within the app
from .managers import CustomUserManager

# Utiliy Classes and Functions
class AuditEntry(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_in', ip=ip, username=user.email)

@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    # TODO Implement IP lock out after failed attempts
    AuditEntry.objects.create(action='user_login_failed', username=credentials.get('username', None))

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
    is_online = models.BooleanField(
        default=False
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

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
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
