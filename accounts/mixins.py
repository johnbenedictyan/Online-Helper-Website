# Imports from python

# Imports from django

# Imports from other apps

# Imports from within the app
from .models import Employer

# Utiliy Classes and Functions

# Start of Mixins

class VerifiedEmployerMixin:
    def check_employer(self):
        return Employer.objects.get(
            pk = self.request.user.pk
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.check_employer():
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.check_employer()
