# Django
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.detail import SingleObjectMixin

# From our apps
from .models import (
    EmployerDocBase,
    EmployerExtraInfo,
)

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

class CheckAgencyEmployeePermissionsDocBaseMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        call_dispatch = super().dispatch(request, *args, **kwargs)

        if (
            user.groups.filter(name='Agency Owners').exists()
            or
            user.groups.filter(name='Agency Administrators').exists()
            or (
                user.groups.filter(name='Agency Managers').exists()
                and
                self.get_object().employer.agency_employee.branch
                ==user.agency_employee.branch
            )
            or
            self.get_object().employer.agency_employee==user
        ):
            return call_dispatch
        else:
            return super().handle_no_permission()

class CheckAgencyEmployeePermissionsSubDocMixin(LoginRequiredMixin):
    login_url = reverse_lazy('agency_sign_in')
    permission_denied_message = '''You do not have the necessary access
                                rights to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        call_dispatch = super().dispatch(request, *args, **kwargs)

        if (
            user.groups.filter(name='Agency Owners').exists()
            or
            user.groups.filter(name='Agency Administrators').exists()
            or (
                user.groups.filter(name='Agency Managers').exists()
                and
                self.get_object().employer_doc_base.employer.agency_employee
                .branch==user.agency_employee.branch
            )
            or
            self.get_object().employer_doc_base.employer.agency_employee==user
        ):
            return call_dispatch
        else:
            return super().handle_no_permission()
