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

# from onlinemaid.mixins import (
#     LoginRequiredMixin,
# )


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
    # def dispatch(self, request, *args, **kwargs):
    #     if (
    #         EmployerExtraInfo.objects.get(pk=self.kwargs
    #         .get(self.pk_url_kwarg)).employer_base.pk==
    #         self.kwargs.get('employer_base_pk')
    #     ):
    #         return super().dispatch(request, *args, **kwargs)
    #     else:
    #         return self.handle_no_permission(request)

# Consider inheriting from alternative more appropriate mixin
class CheckEmployerDocBelongsToEmployer(
    UserPassesTestMixin,
    SingleObjectMixin
):
    def test_func(self):
        # current_obj = self.get_object()
        # if (
        #     EmployerDocBase.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        #     .employer.pk==self.kwargs.get('employer_base_pk')
        # ):
        if self.get_object().employer.pk==self.kwargs.get('employer_base_pk'):
            return True
        else:
            return False
