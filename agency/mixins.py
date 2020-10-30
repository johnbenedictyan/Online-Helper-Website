# Imports from python

# Imports from django

# Imports from other apps

# Imports from within the app
from .models import Agency

# Utiliy Classes and Functions

# Start of Mixins

class AgencyVerifiedMixin:
    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.request.user.pk
    )