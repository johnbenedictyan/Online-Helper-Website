# Imports from python

# Imports from django
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

# Imports from other apps
from onlinemaid.mixins import (
    AccessMixin, LoginRequiredMixin, SuperUserRequiredMixin, GroupRequiredMixin
)

# Imports from within the app
from .models import Maid

# Utiliy Classes and Functions

# Start of Mixins

class SpecificAgencyMaidLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using the
                                employee's or Agency owner account
                                associate with this maid to perform 
                                this action'''
                            
    def dispatch(self, request, *args, **kwargs):
        self.request = request

        res = super(SpecificAgencyMaidLoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


        maid_agency = Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        ).agency

        if self.request.user.groups.filter(name='Agency Owners').exists():
            if self.request.user.agency_owner.agency != maid_agency:
                return self.handle_no_permission(request)
        else:
            if self.request.user.agency_employee.agency != maid_agency:
                return self.handle_no_permission(request)
        
        return res