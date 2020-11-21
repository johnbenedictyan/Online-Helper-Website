# Imports from python

# Imports from django
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

# Imports from other apps
from onlinemaid.mixins import (
    AccessMixin, LoginRequiredMixin, SuperUserRequiredMixin, GroupRequiredMixin
)

# Imports from within the app
from .models import Agency, AgencyEmployee, AgencyBranch

# Utiliy Classes and Functions

# Start of Mixins

class OnlineMaidStaffRequiredMixin(SuperUserRequiredMixin):
    permission_denied_message = '''You are required to login as a member of 
                                Online Maid Pte Ltd to perform this action'''

class AgencyLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')

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
    permission_denied_message = '''You are required to login using this
                                employee or branch's Agency owner account to
                                perform this action'''

    def dispatch(self, request, *args, **kwargs):
        self.request = request

        res = super(SpecificAgencyOwnerRequiredMixin, self).dispatch(
            request, *args, **kwargs)

        if self.check_type is None:
            raise ImproperlyConfigured(
                '{0} requires the "check_type" attribute to be '
                'set.'.format(self.__class__.__name__)
            )

        if self.check_type == 'Employee':
            try:
                AgencyEmployee.objects.get(
                    pk = self.kwargs.get(
                        self.pk_url_kwarg
                    ),
                    agency = self.request.user.agency
                )
            except AgencyEmployee.DoesNotExist:
                return self.handle_no_permission(request)

        elif self.check_type == 'Branch':
            try:
                AgencyBranch.objects.get(
                    pk = self.kwargs.get(
                        self.pk_url_kwarg
                    ),
                    agency = self.request.user.agency
                )
            except AgencyBranch.DoesNotExist:
                return self.handle_no_permission(request)

        else:
            raise ImproperlyConfigured(
                '{0} requires the "check_type" attribute to either '
                'branch or employee.'.format(self.__class__.__name__)
            )