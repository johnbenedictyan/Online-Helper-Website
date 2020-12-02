# Django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
    EmployerBaseCreateForm
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
class EmployerBaseCreate(AgencySalesTeamRequiredMixin,CreateView):
    context_object_name = 'employer_base'
    form_class = EmployerBaseCreateForm
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

# Delete Views
