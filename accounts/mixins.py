# Imports from python

# Imports from django
from django.urls import reverse_lazy

# Imports from other apps
from onlinemaid.mixins import GroupRequiredMixin

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

class PotentialEmployerRequiredMixin(GroupRequiredMixin):
    group_required = u"Potential Employers"
    login_url = reverse_lazy('sign_in')
    permission_denied_message = '''You are required to login using a
                                employer's account to perform this action'''