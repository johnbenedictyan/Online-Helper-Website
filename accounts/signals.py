from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import AuditEntry


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


@receiver(post_save)
def user_try_employer_relation(sender, instance, created, **kwargs):
    if created:
        instance.set_employer_relation()
