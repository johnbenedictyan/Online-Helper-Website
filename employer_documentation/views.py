# Django
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.http import FileResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile

# From our apps
from . import models, forms
from .mixins import *
from onlinemaid import constants as om_constants

# Start of Views

# List Views
class EmployerListView(
    LoginByAgencyUserGroupRequiredMixin,
    ListView
):
    model = models.Employer
    ordering = ['employer_name']
    paginate_by = 20

    def get_queryset(self):
        search_terms = self.request.GET.get('search')

        # Filter results by user's search terms
        if search_terms:
            queryset = super().get_queryset().filter(
                Q(employer_name__icontains=search_terms) |
                Q(employer_email__icontains=search_terms) |
                Q(employer_mobile_number__icontains=search_terms)
            )
        else:
            queryset = super().get_queryset()

        # Further filter queryset to only show the employers that current user
        # has necessary permission to access
        if self.agency_user_group==om_constants.AG_OWNERS:
            # If agency owner, return all employers belonging to agency
            return queryset.filter(
                agency_employee__agency
                = self.request.user.agency_owner.agency
            )
        elif self.agency_user_group==om_constants.AG_ADMINS:
            # If agency administrator, return all employers belonging to agency
            return queryset.filter(
                agency_employee__agency
                = self.request.user.agency_employee.agency
            )
        elif self.agency_user_group==om_constants.AG_MANAGERS:
            # If agency manager, return all employers belonging to branch
            return queryset.filter(
                agency_employee__branch
                = self.request.user.agency_employee.branch
            )
        elif self.agency_user_group==om_constants.AG_SALES:
            # If agency owner, return all employers belonging to self
            return queryset.filter(
                agency_employee = self.request.user.agency_employee
            )
        else:
            return self.handle_no_permission()

class DocListView(
    LoginByAgencyUserGroupRequiredMixin,
    ListView
):
    model = models.EmployerDoc
    # template_name = 'employer_documentation/sales_list.html'
    ordering = ['-agreement_date']
    paginate_by = 20
    is_deployed = None

    def get_queryset(self):
        search_terms = self.request.GET.get('search')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        sort_by = self.request.GET.get('sort_by')

        # Sort by dates
        if sort_by:
            # Get field to sort by
            if 'agreement_date' in sort_by:
                sort_field_name = 'agreement_date'
            elif 'fdw_work_commencement_date' in sort_by:
                sort_field_name = 'rn_maidstatus_ed__fdw_work_commencement_date'
            elif 'ipa_date' in sort_by:
                sort_field_name = 'rn_maidstatus_ed__ipa_approval_date'
        
            # Get ascending or descending user selection
            if sort_by.endswith('asc'):
                self.ordering = [sort_field_name]
            elif sort_by.endswith('des'):
                self.ordering = ['-' + sort_field_name]
        else:
            sort_field_name = self.ordering[0].replace('-', '')

        # Get queryset
        queryset = super().get_queryset().filter(
            rn_maidstatus_ed__is_deployed=self.is_deployed
        )

        # Filter results by user's search terms
        if search_terms:
            queryset = queryset.filter(
                Q(case_ref_no__icontains=search_terms) |
                Q(employer__employer_name__icontains=search_terms) |
                Q(employer__employer_email__icontains=search_terms) |
                Q(employer__employer_mobile_number__icontains=search_terms)
            )
        
        # Further filter queryset to only show the employers that current user
        # has necessary permission to access
        if self.agency_user_group==om_constants.AG_OWNERS:
            # If agency owner, return all employers belonging to agency
            queryset = queryset.filter(
                employer__agency_employee__agency
                = self.request.user.agency_owner.agency
            )
        elif self.agency_user_group==om_constants.AG_ADMINS:
            # If agency administrator, return all employers belonging to agency
            queryset = queryset.filter(
                employer__agency_employee__agency
                = self.request.user.agency_employee.agency
            )
        elif self.agency_user_group==om_constants.AG_MANAGERS:
            # If agency manager, return all employers belonging to branch
            queryset = queryset.filter(
                employer__agency_employee__branch
                = self.request.user.agency_employee.branch
            )
        elif self.agency_user_group==om_constants.AG_SALES:
            # If agency owner, return all employers belonging to self
            queryset = queryset.filter(
                employer__agency_employee = self.request.user.agency_employee
            )
        else:
            return self.handle_no_permission()

        # Filter by start and end dates from user input
        if start_date:
            start_date_kwargs = {sort_field_name+'__gte': start_date}
            queryset = queryset.filter(**start_date_kwargs)
        if end_date:
            end_date_kwargs = {sort_field_name+'__lte': end_date}
            queryset = queryset.filter(**end_date_kwargs)

        return queryset

class EmployerDocListView(
    CheckAgencyEmployeePermissionsMixin,
    ListView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_0_pk'
    ordering = ['-agreement_date']

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_queryset(self):
        return super().get_queryset().filter(employer=self.kwargs.get(
            self.pk_url_kwarg))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)
        if self.object.rn_ed_employer.filter(employer=self.object.pk).count():
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(
                reverse(
                    'ed_create_route',
                    kwargs={'level_0_pk': self.object.pk}
                )
            )

# class EmployerPaymentTransactionListView(
#     CheckAgencyEmployeePermissionsMixin,
#     ListView
# ):
#     model = EmployerPaymentTransaction
#     pk_url_kwarg = 'level_1_pk'
#     ordering = ['transaction_date']

#     def get_object(self, *args, **kwargs):
#         self.object = models.EmployerDoc.objects.get(
#             pk=self.kwargs.get(self.pk_url_kwarg)
#         )
#         return self.object

#     def get_queryset(self):
#         return super().get_queryset().filter(employer_doc=self.kwargs.get(
#             self.pk_url_kwarg))

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['object'] = self.object
#         return context

# Detail Views
class EmployerDetailView(
    CheckAgencyEmployeePermissionsMixin,
    DetailView,
):
    model = models.Employer
    pk_url_kwarg = 'level_0_pk'

class EmployerDocDetailView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    DetailView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'

# Create Views
class EmployerCreateView(
    LoginByAgencyUserGroupRequiredMixin,
    CreateView
):
    model = models.Employer
    form_class = forms.EmployerForm
    template_name = 'employer_documentation/crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def form_valid(self, form):
        if self.agency_user_group==om_constants.AG_SALES:
            form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class EmployerSponsorCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CreateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def form_valid(self, form):
        form.instance.employer = models.Employer.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class EmployerJointApplicantCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CreateView
):
    model = models.EmployerJointApplicant
    form_class = forms.EmployerJointApplicantForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def form_valid(self, form):
        form.instance.employer = models.Employer.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class EmployerDocCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CreateView
):
    model = models.EmployerDoc
    form_class = forms.EmployerDocForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        context['object'] = self.object
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    # def form_valid(self, form):
    #     form.instance.employer = models.Employer.objects.get(
    #         pk = self.kwargs.get(self.pk_url_kwarg)
    #     )
    #     if form.instance.fdw_clean_window_exterior==False:
    #         form.instance.window_exterior_location = None
    #         form.instance.grilles_installed_require_cleaning = None
    #         form.instance.adult_supervision = None

    #     elif not form.instance.window_exterior_location=='OTHER':
    #         form.instance.grilles_installed_require_cleaning = None
    #         form.instance.adult_supervision = None

    #     elif not form.instance.grilles_installed_require_cleaning:
    #         form.instance.adult_supervision = None

    #     return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class DocServiceFeeScheduleCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    CreateView
):
    model = models.DocServiceFeeSchedule
    form_class = forms.DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class DocServiceAgreementCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    CreateView
):
    model = models.DocServiceAgreement
    form_class = forms.DocServiceAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class DocEmploymentContractCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    CreateView
):
    model = models.DocEmploymentContract
    form_class = forms.DocEmploymentContractForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class DocSafetyAgreementCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    CreateView
):
    model = models.DocSafetyAgreement
    form_class = forms.DocSafetyAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

# class EmployerPaymentTransactionCreateView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     CreateView
# ):
#     model = EmployerPaymentTransaction
#     form_class = EmployerPaymentTransactionForm
#     pk_url_kwarg = 'level_1_pk'
#     template_name = 'employer_documentation/crispy_form.html'
#     success_url = reverse_lazy('sales_list_route')

#     def get_object(self, *args, **kwargs):
#         return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['agency_user_group'] = self.agency_user_group
#         return kwargs

#     def form_valid(self, form):
#         form.instance.employer_doc = models.EmployerDoc.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# Update Views
class EmployerUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    UpdateView
):
    model = models.Employer
    form_class = forms.EmployerForm
    template_name = 'employer_documentation/crispy_form.html'
    pk_url_kwarg = 'level_0_pk'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

class EmployerSponsorUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class EmployerDocJointApplicantUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = models.EmployerJointApplicant
    form_class = forms.EmployerJointApplicantForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

class EmployerDocUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = models.EmployerDoc
    form_class = forms.EmployerDocForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get_success_url(self):
        return reverse_lazy('employer_list_route')
    
class DocServiceFeeScheduleUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = models.DocServiceFeeSchedule
    form_class = forms.DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_2_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_success_url(self):
        return reverse_lazy('employer_list_route')

# class EmployerDocSigSlugUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocSig
#     form_class = EmployerDocSigSlugForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/crispy_form.html'
#     model_field_name = None # Aslog in urls.py
#     form_fields = None # Aslog in urls.py
#     success_url_route_name = None # Aslog in urls.py

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['model_field_name'] = self.model_field_name
#         kwargs['form_fields'] = self.form_fields
#         return kwargs

#     def get_success_url(self):
#         return reverse_lazy(self.success_url_route_name, kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#             'level_2_pk': self.object.pk,
#         })

# class EmployerDocMaidStatusUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocMaidStatus
#     form_class = EmployerDocMaidStatusForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/crispy_form.html'

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['agency_user_group'] = self.agency_user_group
#         return kwargs

#     def get_success_url(self):
#         return reverse_lazy('ed_detail_route', kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#         })

# class EmployerDocMaidDeploymentUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocMaidStatus
#     form_class = EmployerDocMaidDeploymentForm
#     pk_url_kwarg = 'level_2_pk'

#     def get_success_url(self):
#         if self.object.is_deployed:
#             return reverse_lazy('status_list_route')
#         else:
#             return reverse_lazy('sales_list_route')

# class JobOrderUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     UpdateView
# ):
#     model = JobOrder
#     form_class = JobOrderForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/joborder_form.html'
#     success_url = reverse_lazy('employer_list_route')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['agency_user_group'] = self.agency_user_group
#         return kwargs

#     def get_success_url(self):
#         return reverse_lazy('ed_detail_route', kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#         })

# class EmployerPaymentTransactionUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     UpdateView
# ):
#     model = EmployerPaymentTransaction
#     form_class = EmployerPaymentTransactionForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/crispy_form.html'
#     success_url = reverse_lazy('sales_list_route')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['agency_user_group'] = self.agency_user_group
#         return kwargs


# Delete Views
class EmployerDeleteView(
    CheckUserIsAgencyOwnerMixin,
    DeleteView
):
    model = models.Employer
    pk_url_kwarg = 'level_0_pk'
    success_url = reverse_lazy('employer_list_route')

# class EmployerDocDeleteView(
#     CheckUserIsAgencyOwnerMixin,
#     CheckEmployerDocRelationshipsMixin,
#     DeleteView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_1_pk'
#     template_name = 'employer_documentation/employer_confirm_delete.html'
#     success_url = reverse_lazy('employer_list_route')


# Signature Views
# class SignatureUpdateByAgentView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocSig
#     form_class = SignatureForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/signature_form_agency.html'
#     model_field_name = None
#     form_fields = None

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['model_field_name'] = self.model_field_name
#         kwargs['form_fields'] = self.form_fields
#         return kwargs

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['model_field_verbose_name'] = EmployerDocSig._meta.get_field(
#             self.model_field_name).verbose_name
#         return context

#     def get_success_url(self):
#         return reverse_lazy('ed_detail_route', kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#         })

# class VerifyUserTokenView(
#     SuccessMessageMixin,
#     UpdateView
# ):
#     model = models.EmployerDocSig
#     form_class = VerifyUserTokenForm
#     template_name = 'employer_documentation/token_form.html'
#     token_field_name = None # Assign this value in urls.py
#     success_url_route_name = None # Assign this value in urls.py
#     success_message = None # Assign this value in urls.py

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['slug'] = self.kwargs.get(self.slug_url_kwarg)
#         kwargs['session'] = self.request.session
#         kwargs['token_field_name'] = self.token_field_name
#         return kwargs

#     def get_success_url(self):
#         if self.success_url_route_name:
#             if self.token_field_name=='employer_token':
#                 slug = self.object.employer_slug
#             elif self.token_field_name=='fdw_token':
#                 slug = self.object.fdw_slug
#         else:
#             return reverse_lazy('home')
#         return reverse_lazy(self.success_url_route_name, kwargs={'slug':slug})

#     def get_success_message(self, cleaned_data):
#         return self.success_message % dict(cleaned_data,)

# class SignatureUpdateByTokenView(
#     SuccessMessageMixin,
#     CheckSignatureSessionTokenMixin,
#     UpdateView
# ):
#     model = models.EmployerDocSig
#     form_class = SignatureForm
#     template_name = 'employer_documentation/signature_form_token.html'
#     model_field_name = None # Assign this value in urls.py
#     token_field_name = None # Assign this value in urls.py
#     form_fields = None # Assign this value in urls.py
#     success_url_route_name = None # Assign this value in urls.py
#     success_message = None # Assign this value in urls.py

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['model_field_name'] = self.model_field_name
#         kwargs['form_fields'] = self.form_fields
#         return kwargs

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['model_field_verbose_name'] = EmployerDocSig._meta.get_field(
#             self.model_field_name).verbose_name
#         return context

#     def get_success_url(self):
#         if self.success_url_route_name:
#             if self.token_field_name=='employer_token':
#                 slug = self.object.employer_slug
#             elif self.token_field_name=='fdw_token':
#                 slug = self.object.fdw_slug
#         else:
#             return reverse_lazy('home')
        
#         if (
#             self.success_url_route_name=='token_signature_employer_spouse_route'
#             and not self.object.employer_doc.spouse_required
#         ):
#             return reverse_lazy('home')
#         else:
#             return reverse_lazy(
#                 self.success_url_route_name,
#                 kwargs={'slug':slug}
#             )

#     def get_success_message(self, cleaned_data):
#         return self.success_message % dict(cleaned_data,)


# PDF Views
# class PdfGenericAgencyView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     PdfHtmlViewMixin,
#     DetailView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_1_pk'

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data()

#         if self.use_repayment_table:
#             context['repayment_table'] = self.calc_repayment_schedule()
        
#         context['url_name'] = request.resolver_match.url_name
#         return self.generate_pdf_response(request, context)

# class PdfFileAgencyView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     DetailView
# ):
#     # model = None # To be passed as parameter in urls.py
#     # pk_url_kwarg = None # To be passed as parameter in urls.py
#     # slug_url_kwarg = None # To be passed as parameter in urls.py
#     as_attachment=False
#     filename='document.pdf'
#     field_name = None

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if isinstance(self.object, JobOrder):
#             try:
#                 return FileResponse(
#                     self.object.job_order_pdf.open(),
#                     as_attachment=self.as_attachment,
#                     filename=self.filename,
#                     content_type='application/pdf'
#                 )
#             except Exception:
#                 return HttpResponseRedirect(
#                     reverse('joborder_update_route', kwargs={
#                         'level_0_pk': self.object.employer_doc.employer.pk,
#                         'level_1_pk': self.object.employer_doc.pk,
#                         'level_2_pk': self.object.pk,
#                 }))
#         elif isinstance(self.object, EmployerDoc):
#             try:
#                 return FileResponse(
#                     getattr(self.object.rn_pdfarchive_ed, self.field_name).open(),
#                     as_attachment=self.as_attachment,
#                     filename=self.filename,
#                     content_type='application/pdf'
#                 )
#             except Exception:
#                 return HttpResponseRedirect(
#                     reverse('pdf_archive_detail', kwargs={
#                         'level_0_pk': self.object.employer.pk,
#                         'level_1_pk': self.object.pk,
#                 }))

# class PdfGenericTokenView(
#     CheckSignatureSessionTokenMixin,
#     PdfHtmlViewMixin,
#     DetailView
# ):
#     model = models.EmployerDocSig
#     slug_url_kwarg = 'slug'
#     token_field_name = None

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data()

#         if self.use_repayment_table:
#             context['repayment_table'] = self.calc_repayment_schedule()

#         return self.generate_pdf_response(request, context)

# class PdfFileTokenView(
#     CheckSignatureSessionTokenMixin,
#     DetailView
# ):
#     model = models.EmployerDocSig
#     slug_url_kwarg = 'slug'
#     token_field_name = None
#     as_attachment=False
#     filename='document.pdf'

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object().employer_doc.rn_joborder_ed
#         try:
#             return FileResponse(
#                 open(self.object.job_order_pdf.path, 'rb'),
#                 as_attachment=self.as_attachment,
#                 filename=self.filename,
#                 content_type='application/pdf'
#             )
#         except Exception:
#             return HttpResponseRedirect(reverse('home'))

# class PdfArchiveSaveView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     PdfHtmlViewMixin,
#     DetailView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_1_pk'

#     def check_signatures(self, employer_doc):
#         if (
#             not employer_doc.rn_signatures_ed.employer_signature or
#             not employer_doc.rn_signatures_ed.fdw_signature or
#             not employer_doc.rn_signatures_ed.agency_staff_signature or
#             not employer_doc.rn_signatures_ed.employer_witness_signature or
#             not employer_doc.rn_signatures_ed.employer_witness_name or
#             not employer_doc.rn_signatures_ed.employer_witness_nric or
#             not employer_doc.rn_signatures_ed.fdw_witness_signature or
#             not employer_doc.rn_signatures_ed.fdw_witness_name or
#             not employer_doc.rn_signatures_ed.fdw_witness_nric or
#             not employer_doc.rn_signatures_ed.agency_staff_witness_signature or
#             not employer_doc.rn_signatures_ed.agency_staff_witness_name or
#             not employer_doc.rn_signatures_ed.agency_staff_witness_nric
#         ):
#             return 'Missing required signatures or witness details.'
        
#         if (
#             employer_doc.spouse_required and (
#                 not employer_doc.rn_signatures_ed.spouse_signature or
#                 not employer_doc.rn_signatures_ed.spouse_name or
#                 not employer_doc.rn_signatures_ed.spouse_nric
#             )
#         ):
#             return 'Missing spouse signature and/or details.'

#         if (
#             employer_doc.sponsor_required and (
#                 not employer_doc.rn_signatures_ed.sponsor_signature or
#                 not employer_doc.rn_signatures_ed.sponsor_name or
#                 not employer_doc.rn_signatures_ed.sponsor_nric
#             )
#         ):
#             return 'Missing sponsor signature and/or details.'
        
#         return False


#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data()
#         context['repayment_table'] = self.calc_repayment_schedule()

#         signatures_check = self.check_signatures(self.object)
#         if signatures_check:
#             messages.add_message(
#                 request,
#                 messages.WARNING,
#                 'Could not save documents. ' + signatures_check
#             )
#             return HttpResponseRedirect(reverse_lazy('sales_list_route'))

#         instance = PdfArchive.objects.get(employer_doc=self.object)
#         folder = 'employer_documentation/pdf/'
#         templates = {
#             'f01_service_fee_schedule':     folder + '01-service-fee-schedule.html',
#             'f03_service_agreement':        folder + '03-service-agreement.html',
#             'f04_employment_contract':      folder + '04-employment-contract.html',
#             'f05_repayment_schedule':       folder + '05-repayment-schedule.html',
#             'f06_rest_day_agreement':       folder + '06-rest-day-agreement.html',
#             'f08_handover_checklist':       folder + '08-handover-checklist.html',
#             'f09_transfer_consent':         folder + '09-transfer-consent.html',
#             'f10_work_pass_authorisation':  folder + '10-work-pass-authorisation.html',
#             # 'f11_security_bond':            folder + '11-security-bond.html',
#             # 'f12_fdw_work_permit':          folder + '12-fdw-work-permit.html',
#             'f13_income_tax_declaration':   folder + '13-income-tax-declaration.html',
#             'f14_safety_agreement':         folder + '14-safety-agreement.html',
#         }
#         for field_name, template_name in templates.items():
#             # filename = template_name.split('/')[-1].split('.')[-2] + '.pdf'
#             filename = field_name + '.pdf'
#             relative_path = f'{self.object.pk}:{filename}'
#             pdf_file = self.generate_pdf_file(request, context, template_name)
#             file_wrapper = SimpleUploadedFile(
#                 relative_path,
#                 pdf_file,
#                 'application/pdf'
#             )
#             setattr(instance, field_name, file_wrapper)
#         instance.save()

#         return HttpResponseRedirect(reverse_lazy('sales_list_route'))

# class PdfArchiveDetailView(
#     CheckAgencyEmployeePermissionsMixin,
#     CheckEmployerDocRelationshipsMixin,
#     DetailView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_1_pk'
#     template_name = 'employer_documentation/pdfarchive_detail.html'
