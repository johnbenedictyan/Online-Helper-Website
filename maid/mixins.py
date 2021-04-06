# Imports from python

# Imports from django
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

# Imports from other apps
from onlinemaid.mixins import (
    LoginRequiredMixin
)
from agency.models import Agency
from agency.mixins import AgencyOwnerRequiredMixin

# Imports from within the app
from .models import (
    Maid, MaidFoodHandlingPreference, MaidDietaryRestriction, 
    MaidEmploymentHistory
)

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

class SpecificAgencyOwnerRequiredMixin(AgencyOwnerRequiredMixin):
    check_type = None
    check_model_dict = {
        'maid': Maid,
        'food_handling_preference': MaidFoodHandlingPreference,
        'dietary_restriction': MaidDietaryRestriction,
        'employment_history': MaidEmploymentHistory
    }
    permission_denied_message = '''You are required to login using the specific
                                Agency owner account to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        self.request = request

        res = super(SpecificAgencyOwnerRequiredMixin, self).dispatch(
            request, *args, **kwargs)

        error_msg = None
        if not self.check_type:
            error_msg = 'set'
        if self.check_type not in self.check_model_dict:
            error_msg = 'a key in the check_model_dict'

        if error_msg:
            raise ImproperlyConfigured(
                '{0} requires the "check_type" attribute to be '
                '{1}.'.format(self.__class__.__name__, error_msg)
            )

        check_model = self.check_model_dict[self.check_type]

        try:
            if self.check_type == 'maid':
                check_model.objects.get(
                    pk = self.kwargs.get(
                        self.pk_url_kwarg
                    ),
                    agency = self.request.user.agency_owner.agency
                )
            else:
                check_model.objects.get(
                    pk = self.kwargs.get(
                        self.pk_url_kwarg
                    ),
                    maid__agency = self.request.user.agency_owner.agency
                )
        except check_model.DoesNotExist:
            return self.handle_no_permission(request)
        else:
            return res

class FDWLimitMixin():
    def dispatch(self, request, *args, **kwargs):
        agency = Agency.objects.get(pk=self.agency_id)
        if agency.get_biodata_limit_status() == True:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.warning(
                self.request,
                'You have reached the limit of FDW Biodata',
                extra_tags='error'
            )
            return redirect('dashboard_maid_list')
                