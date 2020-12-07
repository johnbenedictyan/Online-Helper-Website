# Django
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.detail import SingleObjectMixin

# From our apps
from .models import (
    EmployerBase,
    EmployerDocBase,
    EmployerExtraInfo,
)
from agency.models import AgencyEmployee

# Constants
agency_owners = 'Agency Owners'
agency_administrators = 'Agency Administrators'
agency_managers = 'Agency Managers'
agency_sales_team = 'Agency Sales Team'

# Start of mixins
class CheckEmployerExtraInfoBelongsToEmployerMixin(
    UserPassesTestMixin,
    SingleObjectMixin
):
    def test_func(self):
        test_obj = EmployerExtraInfo.objects.get(
            pk=self.kwargs.get('employer_extra_info_pk')
        )
        if self.get_object().employer_base.pk==self.kwargs.get(
            'employer_base_pk'):
            return True
        else:
            return False

class CheckEmployerDocBaseBelongsToEmployerMixin(
    UserPassesTestMixin,
    SingleObjectMixin
):
    def test_func(self):
        test_obj = EmployerDocBase.objects.get(
            pk=self.kwargs.get('employer_doc_base_pk')
        )
        if test_obj.employer.pk==self.kwargs.get('employer_base_pk'):
            return True
        else:
            return False

class CheckEmployerSubDocBelongsToEmployerMixin(
    UserPassesTestMixin,
    SingleObjectMixin
):
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

class CheckAgencyEmployeePermissionsEmployerBaseMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user_obj = AgencyEmployee.objects.get(pk=request.user.pk)
        test_obj = EmployerBase.objects.get(
            pk=self.kwargs.get('employer_base_pk')
        )
        
        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                test_obj.agency_employee.branch
                ==user_obj.branch
            )
            or
            test_obj.agency_employee==user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return super().handle_no_permission()

class CheckAgencyEmployeePermissionsEmployerExtraInfoMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user_obj = AgencyEmployee.objects.get(pk=request.user.pk)
        test_obj = EmployerExtraInfo.objects.get(
            pk=self.kwargs.get('employer_extra_info_pk')
        )

        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                test_obj.employer_base.agency_employee.branch
                ==user_obj.branch
            )
            or
            test_obj.employer_base.agency_employee==user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return super().handle_no_permission()

class CheckAgencyEmployeePermissionsDocBaseMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user_obj = AgencyEmployee.objects.get(pk=request.user.pk)
        test_obj = EmployerDocBase.objects.get(
            pk=self.kwargs.get('employer_doc_base_pk')
        )

        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                test_obj.employer.agency_employee.branch
                ==user_obj.branch
            )
            or
            test_obj.employer.agency_employee==user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return super().handle_no_permission()

class CheckAgencyEmployeePermissionsSubDocMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user_obj = AgencyEmployee.objects.get(pk=request.user.pk)

        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or (
                request.user.groups.filter(name=agency_managers).exists()
                and
                self.get_object().employer_doc_base.employer.agency_employee
                .branch==user_obj.branch
            )
            or
            self.get_object().employer_doc_base.employer.agency_employee
            ==user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return super().handle_no_permission()

class CheckUserHasAgencyRoleMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if (
            request.user.groups.filter(name=agency_owners).exists()
            or
            request.user.groups.filter(name=agency_administrators).exists()
            or
            request.user.groups.filter(name=agency_managers).exists()
            or
            request.user.groups.filter(name=agency_sales_team).exists()
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return super().handle_no_permission()

class CheckUserIsAgencyOwnerMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.groups.filter(name=agency_owners).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return super().handle_no_permission()
