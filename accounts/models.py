# Imports from python

# Imports from django
from django.db import models
from django.dispatch import receiver
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
    AuditEntry.objects.create(
        action='user_logged_in',
        ip=ip,
        username=user.email
    )


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    # TODO Implement IP lock out after failed attempts
    AuditEntry.objects.create(
        action='user_login_failed',
        username=credentials.get(
            'username',
            None
        )
    )

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
    last_login = models.DateTimeField(
        editable=False,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class PotentialEmployer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Potential Employer'
        verbose_name_plural = 'Potential Employers'
