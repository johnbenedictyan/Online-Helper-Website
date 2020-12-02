# Django
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# 3rd party packages

# From our apps
from .forms import (
    EmployerBaseForm
)

from .models import (
    EmployerBase,
    EmployerDocBase,
    EmployerDocEmploymentContract,
    EmployerDocJobOrder,
    EmployerDocMaidStatus,
    EmployerDocServiceAgreement,
    EmployerDocServiceFeeBase,
    EmployerDocServiceFeeReplacement,
    EmployerDocSig,
    EmployerExtraInfo,
)

from agency.models import AgencyEmployee
from agency.mixins import AgencySalesTeamRequiredMixin


# Start of Views

# Template Views

# Redirect Views

# List Views

# Detail Views
    
# Create Views
class EmployerBaseCreate(AgencySalesTeamRequiredMixin, CreateView):
    form_class = EmployerBaseForm
    http_method_names = ['get','post']
    model = EmployerBase
    template_name = 'create/employer-base-create.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        form.instance.agency_employee = AgencyEmployee.objects.get(
            pk = self.request.user.pk
        )
        return super().form_valid(form)

# Update Views
class EmployerBaseUpdate(AgencySalesTeamRequiredMixin, UpdateView):
    model = EmployerBase
    form_class = EmployerBaseForm
    pk_url_kwarg = 'pk'
    template_name = 'update/employer-base-update.html'
    success_url = reverse_lazy('dashboard_home')

# Delete Views
