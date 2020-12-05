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
    EmployerExtraInfoForm,
    EmployerDocJobOrderForm,
    EmployerDocServiceFeeBaseForm,
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

from .mixins import (
    CheckEmployerExtraInfoBelongsToEmployer,
    CheckEmployerDocBaseBelongsToEmployer,
    CheckEmployerSubDocBelongsToEmployer,
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
class EmployerBaseListView(ListView):
    model = EmployerBase
    ordering = ['employer_name']
    # paginate_by = 10

class EmployerDocBaseListView(ListView):
    model = EmployerDocBase
    pk_url_kwarg = 'employer_base_pk'
    ordering = ['pk']

    def get_queryset(self):
        return super().get_queryset().filter(employer=self.kwargs.get(
            self.pk_url_kwarg))

# Detail Views
class EmployerBaseDetailView(DetailView):
    model = EmployerBase
    pk_url_kwarg = 'employer_base_pk'

class EmployerDocBaseDetailView(
    CheckEmployerDocBaseBelongsToEmployer,
    DetailView
):
    model = EmployerDocBase
    pk_url_kwarg = 'employer_doc_base_pk'

# Create Views
class EmployerBaseCreateView(AgencySalesTeamRequiredMixin, CreateView):
    model = EmployerBase
    form_class = EmployerBaseForm
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        ######## Need to add check that employer/agency combo is unique (try adding UniqueConstraint combo to model) ########
        form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

class EmployerExtraInfoCreateView(AgencySalesTeamRequiredMixin, CreateView):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerExtraInfo
    form_class = EmployerExtraInfoForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        form.instance.employer_base = EmployerBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocBaseCreateView(AgencySalesTeamRequiredMixin, CreateView):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerDocBase
    form_class = EmployerDocBaseForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')

    def form_valid(self, form):
        form.instance.employer = EmployerBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocJobOrderCreateView(
    AgencySalesTeamRequiredMixin,
    CheckEmployerDocBaseBelongsToEmployer,
    CreateView
):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerDocJobOrder
    form_class = EmployerDocJobOrderForm
    pk_url_kwarg = 'employer_doc_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def form_valid(self, form):
        form.instance.employer_doc_base = EmployerDocBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocServiceFeeBaseCreateView(
    AgencySalesTeamRequiredMixin,
    CheckEmployerDocBaseBelongsToEmployer,
    CreateView
):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerDocServiceFeeBase
    form_class = EmployerDocServiceFeeBaseForm
    pk_url_kwarg = 'employer_doc_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def form_valid(self, form):
        form.instance.employer_doc_base = EmployerDocBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)
    ######## Need to add check that agency_employee has necessary permissions before saving ########

# Update Views
class EmployerBaseUpdateView(AgencySalesTeamRequiredMixin, UpdateView):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerBase
    form_class = EmployerBaseForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerExtraInfoUpdateView(
    AgencySalesTeamRequiredMixin,
    CheckEmployerExtraInfoBelongsToEmployer,
    UpdateView
):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerExtraInfo
    form_class = EmployerExtraInfoForm
    pk_url_kwarg = 'employer_extra_info_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocBaseUpdateView(
    AgencySalesTeamRequiredMixin,
    CheckEmployerDocBaseBelongsToEmployer,
    UpdateView
):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerDocBase
    form_class = EmployerDocBaseForm
    pk_url_kwarg = 'employer_doc_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('dashboard_home')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocJobOrderUpdateView(
    AgencySalesTeamRequiredMixin,
    CheckEmployerSubDocBelongsToEmployer,
    UpdateView
):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerDocJobOrder
    form_class = EmployerDocJobOrderForm
    pk_url_kwarg = 'employer_doc_job_order_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocServiceFeeBaseUpdateView(
    AgencySalesTeamRequiredMixin,
    CheckEmployerSubDocBelongsToEmployer,
    UpdateView
):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerDocServiceFeeBase
    form_class = EmployerDocServiceFeeBaseForm
    pk_url_kwarg = 'employer_doc_service_fee_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

# Delete Views
class EmployerBaseDeleteView(AgencyOwnerRequiredMixin, DeleteView):
    model = EmployerBase
    # pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employerbase_confirm_delete.html'
    success_url = reverse_lazy('dashboard_home')
