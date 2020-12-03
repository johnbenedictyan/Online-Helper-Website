# From our apps
from .models import (
    EmployerBase,
    EmployerDocBase,
)

from agency.models import (
    AgencyEmployee,
)

from onlinemaid.mixins import (
    LoginRequiredMixin,
)


# Consider inheriting from alternative more appropriate mixin
class CheckEmployerDocBelongsToEmployer(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if (
            EmployerDocBase.objects.get(pk=self.kwargs.get(self.pk_url_kwarg)).employer.pk==
            self.kwargs.get('employer_base_pk')
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission(request)
