# Django
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# From our apps
from .forms import (
    EmployerBaseForm,
    EmployerDocBaseForm,
    EmployerExtraInfoForm,
    EmployerDocJobOrderForm,
    EmployerDocServiceFeeBaseForm,
    EmployerDocServiceAgreementForm,
    EmployerDocEmploymentContractForm,
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
    CheckEmployerExtraInfoBelongsToEmployerMixin,
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckEmployerSubDocBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    CheckAgencyEmployeePermissionsEmployerExtraInfoMixin,
    CheckAgencyEmployeePermissionsDocBaseMixin,
    CheckAgencyEmployeePermissionsSubDocMixin,
    CheckUserHasAgencyRoleMixin,
)
from agency.mixins import (
    # AgencySalesTeamRequiredMixin,
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

class EmployerDocBaseListView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    ListView
):
    model = EmployerDocBase
    pk_url_kwarg = 'employer_base_pk'
    ordering = ['pk']

    def get_queryset(self):
        return super().get_queryset().filter(employer=self.kwargs.get(
            self.pk_url_kwarg))

# Detail Views
class EmployerBaseDetailView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    DetailView,
):
    model = EmployerBase
    pk_url_kwarg = 'employer_base_pk'

class EmployerDocBaseDetailView(
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsDocBaseMixin,
    DetailView
):
    model = EmployerDocBase
    pk_url_kwarg = 'employer_doc_base_pk'

# Create Views
class EmployerBaseCreateView(
    CheckUserHasAgencyRoleMixin,
    CreateView
):
    model = EmployerBase
    form_class = EmployerBaseForm
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def form_valid(self, form):
        ######## Need to add check that employer/agency combo is unique (try adding UniqueConstraint combo to model) ########
        form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

class EmployerExtraInfoCreateView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    CreateView
):
    model = EmployerExtraInfo
    form_class = EmployerExtraInfoForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def form_valid(self, form):
        form.instance.employer_base = EmployerBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocBaseCreateView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    CreateView
):
    model = EmployerDocBase
    form_class = EmployerDocBaseForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def form_valid(self, form):
        form.instance.employer = EmployerBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocJobOrderCreateView(
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsDocBaseMixin,
    CreateView
):
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
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsDocBaseMixin,
    CreateView
):
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

class EmployerDocServiceAgreementCreateView(
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsDocBaseMixin,
    CreateView
):
    model = EmployerDocServiceAgreement
    form_class = EmployerDocServiceAgreementForm
    pk_url_kwarg = 'employer_doc_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def form_valid(self, form):
        form.instance.employer_doc_base = EmployerDocBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocEmploymentContractCreateView(
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsDocBaseMixin,
    CreateView
):
    model = EmployerDocEmploymentContract
    form_class = EmployerDocEmploymentContractForm
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
class EmployerBaseUpdateView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    UpdateView
):
    ######## Need to change to another permissions mixin to check agency_employee is assigned to employer or has higher level access rights ########
    model = EmployerBase
    form_class = EmployerBaseForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerExtraInfoUpdateView(
    CheckAgencyEmployeePermissionsEmployerExtraInfoMixin,
    CheckEmployerExtraInfoBelongsToEmployerMixin,
    UpdateView
):
    model = EmployerExtraInfo
    form_class = EmployerExtraInfoForm
    pk_url_kwarg = 'employer_extra_info_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocBaseUpdateView(
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsDocBaseMixin,
    UpdateView
):
    model = EmployerDocBase
    form_class = EmployerDocBaseForm
    pk_url_kwarg = 'employer_doc_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocJobOrderUpdateView(
    CheckEmployerSubDocBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsSubDocMixin,
    UpdateView
):
    model = EmployerDocJobOrder
    form_class = EmployerDocJobOrderForm
    pk_url_kwarg = 'employer_doc_job_order_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocServiceFeeBaseUpdateView(
    CheckEmployerSubDocBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsSubDocMixin,
    UpdateView
):
    model = EmployerDocServiceFeeBase
    form_class = EmployerDocServiceFeeBaseForm
    pk_url_kwarg = 'employer_doc_service_fee_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocServiceAgreementUpdateView(
    CheckEmployerSubDocBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsSubDocMixin,
    UpdateView
):
    model = EmployerDocServiceAgreement
    form_class = EmployerDocServiceAgreementForm
    pk_url_kwarg = 'employer_doc_service_agreement_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

class EmployerDocEmploymentContractUpdateView(
    CheckEmployerSubDocBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsSubDocMixin,
    UpdateView
):
    model = EmployerDocEmploymentContract
    form_class = EmployerDocEmploymentContractForm
    pk_url_kwarg = 'employer_doc_employment_contract_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')
    ######## Need to add check that agency_employee has necessary permissions before saving ########

# Delete Views
class EmployerBaseDeleteView(AgencyOwnerRequiredMixin, DeleteView):
    model = EmployerBase
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employerbase_confirm_delete.html'
    success_url = reverse_lazy('employer_base_list')

class EmployerDocBaseDeleteView(
    CheckEmployerDocBaseBelongsToEmployerMixin,
    AgencyOwnerRequiredMixin,
    DeleteView
):
    model = EmployerDocBase
    pk_url_kwarg = 'employer_doc_base_pk'
    template_name = 'employer_documentation/employerbase_confirm_delete.html'
    success_url = reverse_lazy('employer_base_list')
