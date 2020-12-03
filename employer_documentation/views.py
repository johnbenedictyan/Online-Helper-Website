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
    EmployerBaseForm,
    EmployerDocBaseForm,
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
from agency.mixins import (
    AgencySalesTeamRequiredMixin,
    AgencyOwnerRequiredMixin,
)


# Start of Views

# Template Views

# Redirect Views

# List Views

# Detail Views
    
# Create Views
class EmployerBaseCreateView(AgencySalesTeamRequiredMixin, CreateView):
    form_class = EmployerBaseForm
    model = EmployerBase
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        ######## Need to add check that employer/agency combo is unique (try adding UniqueConstraint combo to model) ########
        form.instance.agency_employee = AgencyEmployee.objects.get(
            pk = self.request.user.pk
        )
        return super().form_valid(form)

class EmployerDocBaseCreateView(AgencySalesTeamRequiredMixin, CreateView):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    form_class = EmployerDocBaseForm
    model = EmployerDocBase
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        ######## In form_valid() definition, need to add check that agency_employee has necessary permissions ########
        form.instance.employer = EmployerBase.objects.get(
            pk = self.kwargs[self.pk_url_kwarg]
        )
        return super().form_valid(form)

# Update Views
class EmployerBaseUpdateView(AgencySalesTeamRequiredMixin, UpdateView):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerBase
    form_class = EmployerBaseForm
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')

    ######## In form_valid() definition, need to add check that agency_employee has necessary permissions ########

# Delete Views
class EmployerBaseDeleteView(AgencyOwnerRequiredMixin, DeleteView):
    model = EmployerBase
    template_name = 'employer_documentation/employerbase_confirm_delete.html'
    success_url = reverse_lazy('dashboard_home')
