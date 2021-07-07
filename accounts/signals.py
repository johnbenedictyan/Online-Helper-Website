# Imports from python
from django.utils import timezone

# Imports from django
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

# Imports from other apps

# Imports from within the app

# Start of Signals


@receiver(user_logged_in)
def set_last_login(sender, user, request, **kwargs):
    user.last_login = timezone.now()
    user.save()
