# Imports from python

# Imports from django
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

# Imports from other apps
from onlinemaid.mixins import (
    AccessMixin, LoginRequiredMixin, SuperUserRequiredMixin, GroupRequiredMixin
)
from maid.models import Maid

# Imports from within the app
from .models import Agency, AgencyEmployee, AgencyBranch, AgencyPlan

# Utiliy Classes and Functions

# Start of Mixins

class OnlineMaidStaffRequiredMixin(SuperUserRequiredMixin):
    permission_denied_message = '''You are required to login as a member of 
                                Online Maid Pte Ltd to perform this action'''

class AgencyLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')

    def dispatch(self, request, *args, **kwargs):
        ## Superuser should not have the permssion to access agency views.
        ## It will also mess up the get authority mixin
        if request.user.is_superuser:
            return self.handle_no_permission(request)

        return super(AgencyLoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)

    # This mixin is the base mixin if we want the user to login in using the 
    # agency sign in page rather than the sign in page for the potential 
    # employers.

class AgencyOwnerRequiredMixin(GroupRequiredMixin):
    group_required = u"Agency Owners"
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using an Agency
                                owners account to perform this action'''
                                
class AgencyAdministratorRequiredMixin(GroupRequiredMixin):
    group_required = u"Agency Administrators"
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using an Agency
                                administrator account to perform this 
                                action'''

class AgencyManagerRequiredMixin(GroupRequiredMixin):
    group_required = u"Agency Managers"
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using an Agency
                                managers account to perform this action'''

class AgencyAdminTeamRequiredMixin(GroupRequiredMixin):
    group_required = [u"Agency Owners", u"Agency Administrators"]
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using either
                                an Agency owner or administrator account 
                                to perform this action'''

class AgencySalesTeamRequiredMixin(GroupRequiredMixin):
    group_required = [
        u"Agency Administrators",
        u"Agency Managers",
        u"Agency Sales Team"
    ]
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using either
                                an Agency administrator, manager or sales staff
                                account to perform this action'''

class SpecificAgencyOwnerRequiredMixin(AgencyOwnerRequiredMixin):
    check_type = None
    check_model_dict = {
        'employee': AgencyEmployee,
        'branch': AgencyBranch,
        'plan': AgencyPlan
    }
    permission_denied_message = '''You are required to login using the specific
                                Agency owner account to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        self.request = request

        res = super(SpecificAgencyOwnerRequiredMixin, self).dispatch(
            request, *args, **kwargs)

        if self.check_type is None:
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
            check_model.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                ),
                agency = self.request.user.agency_owner.agency
            )
        except check_model.DoesNotExist:
            return self.handle_no_permission(request)

class SpecificAgencyEmployeeLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using this
                                employee's or Agency owner account to
                                perform this action'''
                            
    def dispatch(self, request, *args, **kwargs):
        self.request = request

        res = super(SpecificAgencyEmployeeLoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)

        if not (
            self.request.user.groups.filter(name='Agency Owners').exists()
            or self.request.user.pk == self.kwargs.get(
                self.pk_url_kwarg
            )
        ):
            return self.handle_no_permission(request)
        
        return res

class GetAuthorityMixin:
    def get_authority(self):
        if self.request.user.groups.filter(name='Agency Owners').exists():
            authority = 'owner'

        if self.request.user.groups.filter(name='Agency Administrators').exists():
            authority = 'administrator'

        if self.request.user.groups.filter(name='Agency Managers').exists():
            authority = 'manager'

        if self.request.user.groups.filter(name='Agency Sales Staff').exists():
            authority = 'sales_staff'

        return authority

    def get(self, request, *args, **kwargs):
        if not self.authority and self.authority != '':
            raise ImproperlyConfigured(
                '{0} is missing the authority attribute'
                .format(self.__class__.__name__)
            )
        self.authority = self.get_authority()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.authority and self.authority != '':
            raise ImproperlyConfigured(
                '{0} is missing the authority attribute'
                .format(self.__class__.__name__)
            )
        self.authority = self.get_authority()
        return super().post(request, *args, **kwargs)