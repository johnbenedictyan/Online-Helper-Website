# Django
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.detail import SingleObjectMixin

# From our apps
from .models import (
    EmployerDocBase,
    EmployerExtraInfo,
)

class CheckEmployerExtraInfoBelongsToEmployer(
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

class CheckEmployerDocBaseBelongsToEmployer(
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

class CheckEmployerSubDocBelongsToEmployer(
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
