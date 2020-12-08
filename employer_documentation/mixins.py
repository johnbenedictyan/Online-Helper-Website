# Django
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

# From our apps
from .models import (
    EmployerBase,
    EmployerDocBase,
    EmployerExtraInfo,
)
from accounts.models import User
from agency.models import (
    AgencyEmployee,
    AgencyOwner,
)

# Constants
agency_owners = 'Agency Owners'
agency_administrators = 'Agency Administrators'
agency_managers = 'Agency Managers'
agency_sales_team = 'Agency Sales Staff'

# Start of mixins
class CheckEmployerExtraInfoBelongsToEmployerMixin(UserPassesTestMixin):
    def test_func(self):
        test_obj = EmployerExtraInfo.objects.get(
            pk=self.kwargs.get('employer_extra_info_pk')
        )
        if self.get_object().employer_base.pk==self.kwargs.get(
            'employer_base_pk'):
            return True
        else:
            return False

class CheckEmployerDocBaseBelongsToEmployerMixin(UserPassesTestMixin):
    def test_func(self):
        test_obj = EmployerDocBase.objects.get(
            pk=self.kwargs.get('employer_doc_base_pk')
        )
        if test_obj.employer.pk==self.kwargs.get('employer_base_pk'):
            return True
        else:
            return False

class CheckEmployerSubDocBelongsToEmployerMixin(UserPassesTestMixin):
    def test_func(self):
        # Access employer_doc_base object via current view's object
        test_obj = self.get_object().employer_doc_base
        if (
            test_obj.employer.pk==self.kwargs.get('employer_base_pk')
            and
            test_obj.pk==self.kwargs.get('employer_doc_base_pk')
        ):
            return True
        else:
            return False

class LoginByAgencyUserGroupRequiredMixin(LoginRequiredMixin):
    '''
    This is a helper mixin that does not override any inherited methods or
    attributes. Use to add additional functionality to LoginRequiredMixin.
    '''
    agency_user_group = None
    user_obj = None

    # Gets current user's assigned agency group. Needs to be called manually.
    def get_agency_user_group(self):
        # First check if current user is agency_employee or agency_owner.
        # If neither, then permission check failed, no further checks needed.
        if (
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_employee'
            )
            or
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_owner'
            )
        ):
            # Assign current user's agency group to agency_user_group atribute
            if self.request.user.groups.filter(name=agency_owners).exists():
                self.agency_user_group = agency_owners
            elif (
                self.request.user.groups.filter(name=agency_administrators)
                .exists()
            ):
                self.agency_user_group = agency_administrators
            elif (
                self.request.user.groups.filter(name=agency_managers).exists()
            ):
                self.agency_user_group = agency_managers
            elif (
                self.request.user.groups.filter(name=agency_sales_team)
                .exists()
            ):
                self.agency_user_group = agency_sales_team
            else:
                return self.handle_no_permission()
            # If successfully assigned current user's agency group to
            # agency_user_group atribute, return True so this method can also
            # serve as a validation that current user has agency role.
            return True
            
        else:
            return self.handle_no_permission()

    # Gets current user's object. Call get_agency_user_group() first to set
    # agency_user_group attribute
    def get_agency_user_object(self):
        if self.agency_user_group==agency_owners:
            self.user_obj = AgencyOwner.objects.get(pk=self.request.user.pk)
        else:
            self.user_obj = AgencyEmployee.objects.get(
                pk=self.request.user.pk
            )

class CheckAgencyEmployeePermissionsEmployerBaseMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's group and user object
        self.get_agency_user_group()
        self.get_agency_user_object()
        
        test_obj = EmployerBase.objects.get(
            pk=self.kwargs.get('employer_base_pk')
        )
        
        # Check test object's agency is same as current user's agency
        if not test_obj.agency_employee.agency==self.user_obj.agency:
            return self.handle_no_permission()

        # Check user belongs to required group to access view
        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                test_obj.agency_employee.branch==self.user_obj.branch
            )
            or
            test_obj.agency_employee==self.user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckAgencyEmployeePermissionsEmployerExtraInfoMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's group and user object
        self.get_agency_user_group()
        self.get_agency_user_object()
        
        test_obj = EmployerExtraInfo.objects.get(
            pk=self.kwargs.get('employer_extra_info_pk')
        )

        # Check test object's agency is same as current user's agency
        if (
            not test_obj.employer_base.agency_employee.agency
            ==self.user_obj.agency
        ):
            return self.handle_no_permission()

        # Check user belongs to required group to access view
        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                test_obj.employer_base.agency_employee.branch
                ==self.user_obj.branch
            )
            or
            test_obj.employer_base.agency_employee==self.user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckAgencyEmployeePermissionsDocBaseMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's group and user object
        self.get_agency_user_group()
        self.get_agency_user_object()
        
        test_obj = EmployerDocBase.objects.get(
            pk=self.kwargs.get('employer_doc_base_pk')
        )

        # Check test object's agency is same as current user's agency
        if not test_obj.employer.agency_employee.agency==self.user_obj.agency:
            return self.handle_no_permission()

        # Check user belongs to required group to access view
        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                test_obj.employer.agency_employee.branch==self.user_obj.branch
            )
            or
            test_obj.employer.agency_employee==self.user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckAgencyEmployeePermissionsSubDocMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's group and user object
        self.get_agency_user_group()
        self.get_agency_user_object()
        
        # Check test object's agency is same as current user's agency
        if (
            not self.get_object().employer_doc_base.employer.agency_employee
            .agency==self.user_obj.agency
        ):
            return self.handle_no_permission()

        # Check user belongs to required group to access view
        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                self.get_object().employer_doc_base.employer.agency_employee
                .branch==self.user_obj.branch
            )
            or
            self.get_object().employer_doc_base.employer.agency_employee
            ==self.user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckUserHasAgencyRoleMixin(LoginByAgencyUserGroupRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Check user has agency group assigned
        if self.get_agency_user_group():
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckUserIsAgencyOwnerMixin(LoginByAgencyUserGroupRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Get current user's group
        self.get_agency_user_group()
        
        # Check if current user is agency owner
        if self.agency_user_group==agency_owners:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()
