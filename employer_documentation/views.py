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
    EmployerBaseAgentForm,
    EmployerDocBaseForm,
    EmployerExtraInfoForm,
    EmployerDocJobOrderForm,
    EmployerDocServiceFeeBaseForm,
    EmployerDocServiceAgreementForm,
    EmployerDocEmploymentContractForm,
    SignatureEmployerForm,
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
    CheckUserIsAgencyOwnerMixin,
    LoginByAgencyUserGroupRequiredMixin,
    PdfMixin,
)
from agency.models import (
    AgencyEmployee,
    AgencyOwner
)
from . import mixins as e_d_mixins


# Start of Views

# Template Views

# Redirect Views

# List Views
class EmployerBaseListView(
    LoginByAgencyUserGroupRequiredMixin,
    ListView
):
    model = EmployerBase
    ordering = ['employer_name']
    # paginate_by = 10

    # Filter queryset to only show the employers that current user has necessary permission to access
    def get_queryset(self):
        # Get current user's group using LoginByAgencyUserGroupRequiredMixin's get_agency_user_group() method
        self.get_agency_user_group()

        if self.agency_user_group==e_d_mixins.agency_owners:
            # If agency owner, return all employers belonging to agency
            return super().get_queryset().filter(
                agency_employee__agency=AgencyOwner.objects.get(
                    pk=self.request.user.pk).agency
            )
        elif self.agency_user_group==e_d_mixins.agency_administrators:
            # If agency administrator, return all employers belonging to agency
            return super().get_queryset().filter(
                agency_employee__agency=AgencyEmployee.objects.get(
                    pk=self.request.user.pk).agency
            )
        elif self.agency_user_group==e_d_mixins.agency_managers:
            # If agency manager, return all employers belonging to branch
            return super().get_queryset().filter(
                agency_employee__branch=AgencyEmployee.objects.get(
                    pk=self.request.user.pk).branch
            )
        elif self.agency_user_group==e_d_mixins.agency_sales_team:
            # If agency owner, return all employers belonging to self
            return super().get_queryset().filter(
                agency_employee=AgencyEmployee.objects.get(
                    pk=self.request.user.pk)
            )
        else:
            return self.handle_no_permission()

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def form_valid(self, form):
        if self.agency_user_group==e_d_mixins.agency_sales_team:
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

class EmployerDocBaseCreateView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    CreateView
):
    model = EmployerDocBase
    form_class = EmployerDocBaseForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def form_valid(self, form):
        form.instance.employer = EmployerBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

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

# Update Views
class EmployerBaseUpdateView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    UpdateView
):
    model = EmployerBase
    form_class = EmployerBaseForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

class EmployerBaseUpdateAgentView(
    CheckAgencyEmployeePermissionsEmployerBaseMixin,
    UpdateView
):
    model = EmployerBase
    form_class = EmployerBaseAgentForm
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employer-form.html'
    success_url = reverse_lazy('employer_base_list')

    def dispatch(self, request, *args, **kwargs):
        # Call inherited dispatch() method first to perform initial
        # permissions checks and set agency_user_group attribute.
        super().dispatch(request, *args, **kwargs)

        # If current user is part of sales staff group, deny access
        if self.agency_user_group==e_d_mixins.agency_sales_team:
            self.handle_no_permission()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        return kwargs

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

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

# Delete Views
class EmployerBaseDeleteView(CheckUserIsAgencyOwnerMixin, DeleteView):
    model = EmployerBase
    pk_url_kwarg = 'employer_base_pk'
    template_name = 'employer_documentation/employerbase_confirm_delete.html'
    success_url = reverse_lazy('employer_base_list')

class EmployerDocBaseDeleteView(
    CheckEmployerDocBaseBelongsToEmployerMixin,
    CheckUserIsAgencyOwnerMixin,
    DeleteView
):
    model = EmployerDocBase
    pk_url_kwarg = 'employer_doc_base_pk'
    template_name = 'employer_documentation/employerbase_confirm_delete.html'
    success_url = reverse_lazy('employer_base_list')


# PDF Views
class SignatureEmployerCreateView(CreateView):
    model = EmployerDocSig
    form_class = SignatureEmployerForm
    pk_url_kwarg = 'employer_doc_base_pk'
    # template_name = ''
    success_url = reverse_lazy('employer_base_list')

    def form_valid(self, form):
        form.instance.employer_doc_base = EmployerDocBase.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

class PdfDetailView(PdfMixin, DetailView):
    model = EmployerDocSig
    pk_url_kwarg = 'docsig_pk'
    template_name = 'employer_documentation/pdf.html'
    # content_disposition = 'inline; filename="custom-filename.pdf"'
