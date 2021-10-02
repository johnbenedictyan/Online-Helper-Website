# Django Imports
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

# Project Apps Imports
from agency.models import Agency
from onlinemaid.constants import (
    AUTHORITY_GROUPS, AG_OWNERS, AG_ADMINS, AG_MANAGERS, AG_SALES, EMPLOYERS,
    FDW
)
from onlinemaid.mixins import (
    LoginRequiredMixin, SuperUserRequiredMixin, GroupRequiredMixin
)

# App Imports

# Start of Mixins


class OMStaffRequiredMixin(SuperUserRequiredMixin):
    login_url = reverse_lazy('sign_in')
    permission_denied_message = '''You are required to login as a member of
                                Online Maid Pte Ltd to perform this action'''


class AgencyLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')

    def dispatch(self, request, *args, **kwargs):
        # Superuser should not have the permssion to access agency views.
        # It will also mess up the get authority mixin
        if request.user.is_superuser:
            return self.handle_no_permission(request)

        return super(AgencyLoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)

    # This mixin is the base mixin if we want the user to login in using the
    # agency login page rather than the login page for the potential
    # employers.


class AgencyOwnerRequiredMixin(GroupRequiredMixin):
    group_required = AG_OWNERS
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using an Agency
                                owners account to perform this action'''


class AgencyAdministratorRequiredMixin(GroupRequiredMixin):
    group_required = AG_ADMINS
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You are required to login using an Agency
                                administrator account to perform this
                                action'''


class AgencyManagerRequiredMixin(GroupRequiredMixin):
    group_required = AG_MANAGERS
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


class GetAuthorityMixin:
    authority = ''
    agency_id = ''

    def get_authority(self):
        authority = agency_id = ''
        for auth_name in AUTHORITY_GROUPS:
            if self.request.user.groups.filter(name=auth_name).exists():
                authority = auth_name
                if authority == AG_OWNERS:
                    agency_id = self.request.user.agency_owner.agency.pk
                elif authority != EMPLOYERS and authority != FDW:
                    agency_id = self.request.user.agency_employee.agency.pk

        return {
            'authority': authority,
            'agency_id': agency_id
        }

    def dispatch(self, request, *args, **kwargs):
        if not self.authority and self.authority != '':
            raise ImproperlyConfigured(
                '{0} is missing the authority attribute'
                .format(self.__class__.__name__)
            )
        if not self.agency_id and self.agency_id != '':
            raise ImproperlyConfigured(
                '{0} is missing the agency_id attribute'
                .format(self.__class__.__name__)
            )
        self.authority = self.get_authority()['authority']
        self.agency_id = self.get_authority()['agency_id']
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.agency_id != '':
            context.update({
                'agency_name': Agency.objects.get(
                    pk=self.agency_id
                ).name
            })
        return context
