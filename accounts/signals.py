from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.utils import timezone

from .models import AuditEntry

# Start of Signals


@receiver(user_logged_in)
def set_last_login(sender, user, request, **kwargs):
    user.last_login = timezone.now()
    user.save()
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
