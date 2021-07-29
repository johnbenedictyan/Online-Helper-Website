# Django Imports
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

# Project Apps Imports
from accounts.models import User
from onlinemaid.constants import (
    AUTHORITY_GROUPS, AG_OWNERS, AG_ADMINS, AG_MANAGERS, AG_SALES, P_EMPLOYERS
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
    # agency log in page rather than the log in page for the potential
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


class AgencyAccessToEmployerDocAppMixin(AgencyLoginRequiredMixin):
    permission_denied_message = '''Access permission denied'''

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        access_granted = False

        # If URL has pk, then check user access permissions
        if self.kwargs.get(self.pk_url_kwarg):
            # Set agency user object
            test_user = User.objects.get(pk=request.user.pk)
            if hasattr(test_user, 'agency_owner'):
                agency_user_obj = test_user.agency_owner
            elif hasattr(test_user, 'agency_employee'):
                agency_user_obj = test_user.agency_employee
            else:
                agency_user_obj = None

            # Set employer object
            employer_obj = None
            test_obj = self.get_object() if agency_user_obj else None
            if test_obj:
                if hasattr(test_obj, 'applicant_type'):
                    employer_obj = test_obj
                elif hasattr(test_obj, 'employer'):
                    employer_obj = test_obj.employer
                elif hasattr(test_obj, 'employer_doc'):
                    employer_obj = test_obj.employer_doc.employer

            # Check agency user permissions vs employer object
            if (
                employer_obj and
                employer_obj.agency_employee.agency == agency_user_obj.agency
            ):
                if self.authority == AG_OWNERS:
                    access_granted = True
                elif self.authority == AG_ADMINS:
                    access_granted = True  # TODO: Handle no permission
                elif self.authority == AG_MANAGERS:
                    employer_agent = employer_obj.agency_employee
                    if employer_agent.branch == agency_user_obj.branch:
                        access_granted = True
                elif self.authority == AG_SALES:
                    if employer_obj.agency_employee == agency_user_obj:
                        access_granted = True

        # If URL does not have pk, then fall back to inherited dispatch handler
        else:
            access_granted = True

        if access_granted:
            return handler
        else:
            return self.handle_no_permission(request)


class OwnerAccessToEmployerDocAppMixin(AgencyAccessToEmployerDocAppMixin):
    permission_denied_message = '''Access permission denied'''

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        if self.authority == AG_OWNERS:
            return handler
        else:
            self.handle_no_permission(request)


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
                elif authority != P_EMPLOYERS:
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
