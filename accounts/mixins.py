# Imports from python

# Imports from django

# Imports from other apps

# Imports from within the app
from .models import Employer

# Utiliy Classes and Functions

# Start of Mixins

class VerifiedEmployerMixin:
    def get_object(self, queryset=None):
        return Employer.objects.get(
            pk = self.request.user.pk
    )