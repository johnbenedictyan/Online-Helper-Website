# Imports from python

# Imports from django
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.urls import reverse_lazy

# Imports from other apps

# Imports from within the app

# Utiliy Classes and Functions

# Start of Mixins

class SuperUserRequiredMixin(AccessMixin):
    permission_denied_message = '''You are required to login as a member of 
                                Online Maid Pte Ltd to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class AgencyLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')

    # This mixin is the base mixin if we want the user to login in using the 
    # agency sign in page rather than the sign in page for the potential 
    # employers.