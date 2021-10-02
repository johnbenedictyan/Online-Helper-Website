from itertools import chain

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

# Start of Models


class User(AbstractUser):
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

    def __str__(self) -> str:
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

    def __str__(self) -> str:
        return self.user.email

    def get_general_enquiries(self):
        pass

    def get_shortlisted_enquiries(self):
        pass

    def get_enquiries(self):
        return {
            'general': self.get_general_enquiries(),
            'shortlisted': self.get_shortlisted_enquiries()
        }

    def get_documents(self):
        return list(
            chain.from_iterable(
                x.rn_ed_employer.all() for x in self.employers.all()
            )
        )

    class Meta:
        verbose_name = 'Potential Employer'
        verbose_name_plural = 'Potential Employers'


class FDWAccount(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

    def __str__(self) -> str:
        return self.user.email

    class Meta:
        verbose_name = 'Foreign Domestic Worker'
        verbose_name_plural = 'Foreign Domestic Workers'


class AuditEntry(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    username = models.CharField(max_length=256, null=True)

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

    def __str__(self) -> str:
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)

    class Meta:
        verbose_name = 'Audit Entry'
        verbose_name_plural = 'Audit Entries'
