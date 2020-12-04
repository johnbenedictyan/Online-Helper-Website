# Django
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.detail import SingleObjectMixin

# From our apps
from .models import (
    EmployerBase,
    EmployerDocBase,
    EmployerExtraInfo,
)

from agency.models import (
    AgencyEmployee,
)


# Consider inheriting from alternative more appropriate mixin
class CheckEmployerExtraInfoBelongsToEmployer(
    UserPassesTestMixin,
    SingleObjectMixin
):
    def test_func(self):
        if self.get_object().employer_base.pk==self.kwargs.get(
            'employer_base_pk'):
            return True
        else:
            return False

# Consider inheriting from alternative more appropriate mixin
class CheckEmployerDocBelongsToEmployer(
    UserPassesTestMixin,
    SingleObjectMixin
):
    def test_func(self):
        if self.get_object().employer.pk==self.kwargs.get('employer_base_pk'):
            return True
        else:
            return False

class CheckEmployerSubDocBelongsToEmployer(
    UserPassesTestMixin,
    SingleObjectMixin
):
    def test_func(self):
        if (
            self.get_object().employer_doc_base.employer.pk==self.kwargs.get('employer_base_pk')
            and
            self.get_object().employer_doc_base.pk==self.kwargs.get('employer_doc_base_pk')
        ):
            return True
        else:
            return False
