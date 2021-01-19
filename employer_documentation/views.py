# Django
from django.urls import reverse, reverse_lazy
from django.http import FileResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

# From our apps
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
    JobOrder,
)
from .forms import (
    EmployerForm,
    EmployerDocForm,
    EmployerDocLockForm,
    EmployerDocAgreementDateForm,
    EmployerDocSigSlugForm,
    EmployerDocMaidStatusForm,
    JobOrderForm,
    SignatureForm,
    VerifyUserTokenForm,
)
from .mixins import (
    CheckEmployerDocRelationshipsMixin,
    CheckAgencyEmployeePermissionsMixin,
    CheckUserIsAgencyOwnerMixin,
    LoginByAgencyUserGroupRequiredMixin,
    PdfHtmlViewMixin,
    CheckSignatureSessionTokenMixin,
    RepaymentScheduleMixin,
)
from onlinemaid.constants import (
    AG_OWNERS,
    AG_ADMINS,
    AG_MANAGERS,
    AG_SALES,
)


# Start of Views

# List Views
class EmployerListView(
    LoginByAgencyUserGroupRequiredMixin,
    ListView
):
    model = Employer
    ordering = ['employer_name']
    paginate_by = 20

    def get_queryset(self):
        search_terms = self.request.GET.get('search')

        # Filter results by user's search terms
        if search_terms:
            queryset = super().get_queryset().filter(
                Q(employer_name__icontains=search_terms) |
                Q(employer_nric__icontains=search_terms) |
                Q(employer_email__icontains=search_terms) |
                Q(employer_mobile_number__icontains=search_terms)
            )
        else:
            queryset = super().get_queryset()

        # Further filter queryset to only show the employers that current user
        # has necessary permission to access
        if self.agency_user_group==AG_OWNERS:
            # If agency owner, return all employers belonging to agency
            return queryset.filter(
                agency_employee__agency
                = self.request.user.agency_owner.agency
            )
        elif self.agency_user_group==AG_ADMINS:
            # If agency administrator, return all employers belonging to agency
            return queryset.filter(
                agency_employee__agency
                = self.request.user.agency_employee.agency
            )
        elif self.agency_user_group==AG_MANAGERS:
            # If agency manager, return all employers belonging to branch
            return queryset.filter(
                agency_employee__branch
                = self.request.user.agency_employee.branch
            )
        elif self.agency_user_group==AG_SALES:
            # If agency owner, return all employers belonging to self
            return queryset.filter(
                agency_employee = self.request.user.agency_employee
            )
        else:
            return self.handle_no_permission()

class StatusListView(
    LoginByAgencyUserGroupRequiredMixin,
    ListView
):
    model = EmployerDoc
    template_name = 'employer_documentation/status_list.html'
    ordering = ['-agreement_date']
    paginate_by = 20

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
            elif 'ipa_date' in sort_by:
                sort_field_name = 'rn_maidstatus_ed__ipa_approval_date'
        
            # Get ascending or descending user selection
            if sort_by.endswith('asc'):
                self.ordering = [sort_field_name]
            elif sort_by.endswith('des'):
                self.ordering = ['-' + sort_field_name]
        else:
            sort_field_name = self.ordering[0].replace('-', '')

        # Get queryset, but only locked/finalised documents
        queryset = super().get_queryset().filter(is_locked = True)

        # Filter results by user's search terms
        if search_terms:
            queryset = queryset.filter(
                Q(case_ref_no__icontains=search_terms) |
                Q(employer__employer_name__icontains=search_terms) |
                Q(employer__employer_nric__icontains=search_terms) |
                Q(employer__employer_email__icontains=search_terms) |
                Q(employer__employer_mobile_number__icontains=search_terms)
            )
        
        # Further filter queryset to only show the employers that current user
        # has necessary permission to access
        if self.agency_user_group==AG_OWNERS:
            # If agency owner, return all employers belonging to agency
            queryset = queryset.filter(
                employer__agency_employee__agency
                = self.request.user.agency_owner.agency
            )
        elif self.agency_user_group==AG_ADMINS:
            # If agency administrator, return all employers belonging to agency
            queryset = queryset.filter(
                employer__agency_employee__agency
                = self.request.user.agency_employee.agency
            )
        elif self.agency_user_group==AG_MANAGERS:
            # If agency manager, return all employers belonging to branch
            queryset = queryset.filter(
                employer__agency_employee__branch
                = self.request.user.agency_employee.branch
            )
        elif self.agency_user_group==AG_SALES:
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
    model = EmployerDoc
    pk_url_kwarg = 'employer_pk'
    ordering = ['-agreement_date']

    def get_object(self, *args, **kwargs):
        return Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_queryset(self):
        return super().get_queryset().filter(employer=self.kwargs.get(
            self.pk_url_kwarg))

    def get(self, request, *args, **kwargs):
        if self.object.rn_ed_employer.filter(employer=self.object.pk).count():
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(
                reverse(
                    'employerdoc_create_route',
                    kwargs={'employer_pk': self.object.pk}
                )
            )

# Detail Views
class EmployerDetailView(
    CheckAgencyEmployeePermissionsMixin,
    DetailView,
):
    model = Employer
    pk_url_kwarg = 'employer_pk'

class EmployerDocDetailView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'employerdoc_pk'

# Create Views
class EmployerCreateView(
    LoginByAgencyUserGroupRequiredMixin,
    CreateView
):
    model = Employer
    form_class = EmployerForm
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def form_valid(self, form):
        if self.agency_user_group==AG_SALES:
            form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

class EmployerDocCreateView(
    CheckAgencyEmployeePermissionsMixin,
    CreateView
):
    model = EmployerDoc
    form_class = EmployerDocForm
    pk_url_kwarg = 'employer_pk'
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')

    def get_object(self, *args, **kwargs):
        return Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

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

    def form_valid(self, form):
        form.instance.employer = Employer.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

# Update Views
class EmployerUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    UpdateView
):
    model = Employer
    form_class = EmployerForm
    template_name = 'employer_documentation/crispy_form.html'
    pk_url_kwarg = 'employer_pk'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

class EmployerDocUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = EmployerDoc
    form_class = EmployerDocForm
    pk_url_kwarg = 'employerdoc_pk'
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get(self, request, *args, **kwargs):
        if not self.object.is_locked:
            return super().get(request, *args, **kwargs)
        else:
            message = 'The document has been locked from editing'
            messages.error(request, message)
            return HttpResponseRedirect(
                reverse('employerdoc_lock_route', kwargs={
                    'employer_pk': self.object.employer.pk,
                    'employerdoc_pk': self.object.pk,
                })
            )

class EmployerDocLockUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = EmployerDoc
    form_class = EmployerDocLockForm
    pk_url_kwarg = 'employerdoc_pk'
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')

class EmployerDocAgreementDateUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = EmployerDoc
    form_class = EmployerDocAgreementDateForm
    pk_url_kwarg = 'employerdoc_pk'
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')

    def get(self, request, *args, **kwargs):
        if not self.object.is_locked:
            return super().get(request, *args, **kwargs)
        else:
            message = 'The document has been locked from editing'
            messages.error(request, message)
            return HttpResponseRedirect(
                reverse('employerdoc_lock_route', kwargs={
                    'employer_pk': self.object.employer.pk,
                    'employerdoc_pk': self.object.pk,
                })
            )

class EmployerDocSigSlugUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = EmployerDocSig
    form_class = EmployerDocSigSlugForm
    pk_url_kwarg = 'employersubdoc_pk'
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')
    model_field_name = None
    form_fields = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['model_field_name'] = self.model_field_name
        kwargs['form_fields'] = self.form_fields
        return kwargs

    def get(self, request, *args, **kwargs):
        if not self.object.employer_doc.is_locked:
            return super().get(request, *args, **kwargs)
        else:
            message = 'The document has been locked from editing'
            messages.error(request, message)
            return HttpResponseRedirect(
                reverse('employerdoc_lock_route', kwargs={
                    'employer_pk': self.object.employer_doc.employer.pk,
                    'employerdoc_pk': self.object.employer_doc.pk,
                })
            )

class EmployerDocMaidStatusUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = EmployerDocMaidStatus
    form_class = EmployerDocMaidStatusForm
    pk_url_kwarg = 'employersubdoc_pk'
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get(self, request, *args, **kwargs):
        if self.object.employer_doc.is_locked:
            return super().get(request, *args, **kwargs)
        else:
            message = 'The document needs to be finalised and locked from \
                editing before the status can be accessed'
            messages.error(request, message)
            return HttpResponseRedirect(
                reverse('employerdoc_lock_route', kwargs={
                    'employer_pk': self.object.employer_doc.employer.pk,
                    'employerdoc_pk': self.object.employer_doc.pk,
                })
            )

class JobOrderUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = JobOrder
    form_class = JobOrderForm
    pk_url_kwarg = 'employersubdoc_pk'
    template_name = 'employer_documentation/joborder_form.html'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def get(self, request, *args, **kwargs):
        if not self.object.employer_doc.is_locked:
            return super().get(request, *args, **kwargs)
        else:
            message = 'The document has been locked from editing'
            messages.error(request, message)
            return HttpResponseRedirect(
                reverse('employerdoc_lock_route', kwargs={
                    'employer_pk': self.object.employer_doc.employer.pk,
                    'employerdoc_pk': self.object.employer_doc.pk,
                })
            )

# Delete Views
class EmployerDeleteView(
    CheckUserIsAgencyOwnerMixin,
    DeleteView
):
    model = Employer
    pk_url_kwarg = 'employer_pk'
    success_url = reverse_lazy('employer_list_route')

class EmployerDocDeleteView(
    CheckUserIsAgencyOwnerMixin,
    CheckEmployerDocRelationshipsMixin,
    DeleteView
):
    model = EmployerDoc
    pk_url_kwarg = 'employerdoc_pk'
    template_name = 'employer_documentation/employer_confirm_delete.html'
    success_url = reverse_lazy('employer_list_route')


# Signature Views
class SignatureUpdateByAgentView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = EmployerDocSig
    form_class = SignatureForm
    pk_url_kwarg = 'employersubdoc_pk'
    template_name = 'employer_documentation/signature_form_agency.html'
    success_url = reverse_lazy('employer_list_route')
    model_field_name = None
    form_fields = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['model_field_name'] = self.model_field_name
        kwargs['form_fields'] = self.form_fields
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_field_verbose_name'] = EmployerDocSig._meta.get_field(
            self.model_field_name).verbose_name
        return context

    def get(self, request, *args, **kwargs):
        if self.object.employer_doc.is_locked:
            return super().get(request, *args, **kwargs)
        else:
            message = 'The document needs to be finalised and locked from \
                editing before it can be signed'
            messages.error(request, message)
            return HttpResponseRedirect(
                reverse('employerdoc_lock_route', kwargs={
                    'employer_pk': self.object.employer_doc.employer.pk,
                    'employerdoc_pk': self.object.employer_doc.pk,
                })
            )

class VerifyUserTokenView(
    SuccessMessageMixin,
    UpdateView
):
    model = EmployerDocSig
    form_class = VerifyUserTokenForm
    template_name = 'employer_documentation/token_form.html'
    token_field_name = None # Assign this value in urls.py
    success_url_route_name = None # Assign this value in urls.py
    success_message = None # Assign this value in urls.py

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['slug'] = self.kwargs.get(self.slug_url_kwarg)
        kwargs['session'] = self.request.session
        kwargs['token_field_name'] = self.token_field_name
        return kwargs

    def get_success_url(self):
        if self.success_url_route_name:
            if self.token_field_name=='employer_token':
                slug = self.object.employer_slug
            elif self.token_field_name=='fdw_token':
                slug = self.object.fdw_slug
        else:
            return reverse_lazy('home')
        return reverse_lazy(self.success_url_route_name, kwargs={'slug':slug})

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data,)

class SignatureUpdateByTokenView(
    SuccessMessageMixin,
    CheckSignatureSessionTokenMixin,
    UpdateView
):
    model = EmployerDocSig
    form_class = SignatureForm
    template_name = 'employer_documentation/signature_form_token.html'
    model_field_name = None # Assign this value in urls.py
    token_field_name = None # Assign this value in urls.py
    form_fields = None # Assign this value in urls.py
    success_url_route_name = None # Assign this value in urls.py
    success_message = None # Assign this value in urls.py

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['model_field_name'] = self.model_field_name
        kwargs['form_fields'] = self.form_fields
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_field_verbose_name'] = EmployerDocSig._meta.get_field(
            self.model_field_name).verbose_name
        return context

    def get_success_url(self):
        if self.success_url_route_name:
            if self.token_field_name=='employer_token':
                slug = self.object.employer_slug
            elif self.token_field_name=='fdw_token':
                slug = self.object.fdw_slug
        else:
            return reverse_lazy('home')
        return reverse_lazy(self.success_url_route_name, kwargs={'slug':slug})

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data,)


# PDF Views
class PdfGenericAgencyView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'employerdoc_pk'

class PdfServiceAgreementAgencyView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'employerdoc_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agency_main_branch'] = (
            self.object.employer.agency_employee.agency.branches.filter(
                main_branch=True
            ).all()[0]
        )
        return context

class PdfRepaymentScheduleAgencyView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    PdfHtmlViewMixin,
    RepaymentScheduleMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'employerdoc_pk'

class PdfFileAgencyView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    DetailView
):
    model = JobOrder
    slug_url_kwarg = 'slug'
    as_attachment=False
    filename='document.pdf'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return FileResponse(
                open(self.object.job_order_pdf.path, 'rb'),
                as_attachment=self.as_attachment,
                filename=self.filename,
                content_type='application/pdf'
            )
        except:
            return HttpResponseRedirect(
                reverse('joborder_update_route', kwargs={
                    'employer_pk': self.object.employer_doc.employer.pk,
                    'employerdoc_pk': self.object.employer_doc.pk,
                    'employersubdoc_pk': self.object.pk,
            }))

class PdfGenericTokenView(
    CheckSignatureSessionTokenMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = EmployerDocSig
    slug_url_kwarg = 'slug'
    token_field_name = None

class PdfServiceAgreementTokenView(
    CheckSignatureSessionTokenMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = EmployerDocSig
    slug_url_kwarg = 'slug'
    token_field_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agency_main_branch'] = (
            self.object.employer_doc.employer.agency_employee.agency.branches.filter(
                main_branch=True
            ).all()[0]
        )
        return context

class PdfRepaymentScheduleTokenView(
    CheckSignatureSessionTokenMixin,
    PdfHtmlViewMixin,
    RepaymentScheduleMixin,
    DetailView
):
    model = EmployerDocSig
    slug_url_kwarg = 'slug'
    token_field_name = None

    def get_context_data(self, **kwargs):
        # Re-assign self.object to be instance of EmployerDoc object for
        # RepaymentScheduleMixin's calculations
        self.object = self.get_object().employer_doc
        context = super().get_context_data(**kwargs)
        return context

class PdfFileTokenView(
    CheckSignatureSessionTokenMixin,
    DetailView
):
    model = EmployerDocSig
    slug_url_kwarg = 'slug'
    token_field_name = None
    as_attachment=False
    filename='document.pdf'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object().employer_doc.rn_joborder_ed
        print(self.object.job_order_pdf)
        try:
            return FileResponse(
                open(self.object.job_order_pdf.path, 'rb'),
                as_attachment=self.as_attachment,
                filename=self.filename,
                content_type='application/pdf'
            )
        except:
            return HttpResponseRedirect(
                reverse('home'))
