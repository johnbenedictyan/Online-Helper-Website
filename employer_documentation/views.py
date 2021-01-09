# Python
import calendar

# Django
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import FileResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin

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
    EmployerDocAgreementDateForm,
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

class EmployerDocListView(
    CheckAgencyEmployeePermissionsMixin,
    ListView
):
    model = EmployerDoc
    pk_url_kwarg = 'employer_pk'
    ordering = ['pk']

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

class EmployerDocAgreementDateUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    UpdateView
):
    model = EmployerDocSig
    form_class = EmployerDocAgreementDateForm
    pk_url_kwarg = 'employersubdoc_pk'
    template_name = 'employer_documentation/crispy_form.html'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

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
    pk_url_kwarg = 'docsig_pk'
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
class PdfEmployerDocumentView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'employerdoc_pk'

class PdfServiceAgreementView(
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

class PdfRepaymentScheduleView(
    CheckAgencyEmployeePermissionsMixin,
    CheckEmployerDocRelationshipsMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'employerdoc_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repayment_table'] = {}
        today = timezone.now()

        payment_month = today.month
        payment_year = today.year
        placement_fee = (
            self.object.fdw.agency_fee_amount +
            self.object.fdw.personal_loan_amount
        )
        placement_fee_per_month = round(placement_fee/6, 0)
        # work_days_in_month = 30 - self.object.fdw.days_off
        # off_day_compensation = round(
        #     self.object.fdw.salary/work_days_in_month, 0
        # )
        work_days_in_month = 26
        off_day_compensation = round(
            self.object.fdw.salary*self.object.fdw.days_off/work_days_in_month, 0
        )
        salary_per_month = self.object.fdw.salary + off_day_compensation
        
        if (
            self.object.rn_maidstatus_ed.fdw_work_commencement_date
            and
            self.object.rn_maidstatus_ed.fdw_work_commencement_date.day==1
        ):
            # If work start date is 1st of month, then payment does not need
            # to be pro-rated.
            for i in range(1,25):
                month_current = (
                    12 if payment_month%12==0 else payment_month%12
                )
                loan_repaid = min(
                    placement_fee,
                    placement_fee_per_month,
                    salary_per_month
                )

                context['repayment_table'][i] = {
                    'salary_date': '{day}/{month}/{year}'.format(
                        day = calendar.monthrange(
                            payment_year, month_current)[1],
                        month = month_current,
                        year = payment_year,
                    ),
                    'basic_salary': self.object.fdw.salary,
                    'off_day_compensation': off_day_compensation,
                    'salary_per_month': salary_per_month,
                    'salary_received': salary_per_month-loan_repaid,
                    'loan_repaid': loan_repaid
                }
                placement_fee = (
                    placement_fee-loan_repaid
                    if placement_fee-loan_repaid>=0
                    else 0
                )
                payment_month += 1
                if payment_month%12 == 1:
                    payment_year += 1

        if (
            self.object.rn_maidstatus_ed.fdw_work_commencement_date
            and not
            self.object.rn_maidstatus_ed.fdw_work_commencement_date.day==1
        ):
            # Pro-rated payments
            month_current = (
                12 if payment_month%12==0 else payment_month%12
            )
            first_month_days = (
                calendar.monthrange(
                    payment_year, month_current)[1]
                - self.object.rn_maidstatus_ed
                .fdw_work_commencement_date.day + 1
            )
            first_month_salary = round(salary_per_month*first_month_days/
                calendar.monthrange(payment_year, month_current)[1], 0)
            loan_repaid = min(
                placement_fee,
                placement_fee_per_month,
                round(salary_per_month*first_month_days/calendar.monthrange(
                    payment_year, month_current)[1], 0)
            )

            # 1st month pro-rated
            context['repayment_table'][1] = {
                'salary_date': '{day}/{month}/{year}'.format(
                    day = calendar.monthrange(
                        payment_year, month_current)[1],
                    month = month_current,
                    year = payment_year,
                    ),
                'basic_salary': round(
                    self.object.fdw.salary*first_month_days/
                    calendar.monthrange(
                        payment_year, month_current)[1], 0
                ),
                'off_day_compensation': round(
                    off_day_compensation*first_month_days/
                    calendar.monthrange(
                        payment_year, month_current)[1], 0
                ),
                'salary_per_month': first_month_salary,
                'salary_received': first_month_salary - loan_repaid,
                'loan_repaid': loan_repaid
            }
            placement_fee = (
                placement_fee-loan_repaid
                if placement_fee-loan_repaid>=0
                else 0
            )
            payment_month += 1
            if payment_month%12 == 1:
                payment_year += 1

            # 2nd-23rd months of full month payments
            for i in range(2,25):
                month_current = (
                    12 if payment_month%12==0 else payment_month%12
                )
                loan_repaid = min(
                    placement_fee,
                    placement_fee_per_month,
                    salary_per_month
                )

                context['repayment_table'][i] = {
                    'salary_date': '{day}/{month}/{year}'.format(
                        day = calendar.monthrange(
                            payment_year, month_current)[1],
                        month = month_current,
                        year = payment_year,
                    ),
                    'basic_salary': self.object.fdw.salary,
                    'off_day_compensation': off_day_compensation,
                    'salary_per_month': salary_per_month,
                    'salary_received': salary_per_month-loan_repaid,
                    'loan_repaid': loan_repaid
                }
                placement_fee = (
                    placement_fee-loan_repaid
                    if placement_fee-loan_repaid>=0
                    else 0
                )
                payment_month += 1
                if payment_month%12 == 1:
                    payment_year += 1

            # 25th month pro-rated
            final_payment_day = min(
                self.object.rn_maidstatus_ed
                .fdw_work_commencement_date.day-1 ,
                calendar.monthrange(payment_year, month_current)[1]
            )
            basic_salary = round(
                self.object.fdw.salary*final_payment_day/calendar.monthrange(
                    payment_year, month_current)[1]
            )
            off_day_compensation = round(
                off_day_compensation*final_payment_day/calendar.monthrange(
                    payment_year, month_current)[1]
            )
            month_current = 12 if payment_month%12==0 else payment_month%12
            loan_repaid = min(
                placement_fee,
                placement_fee_per_month,
                salary_per_month
            )
            context['repayment_table'][25] = {
                'salary_date': '{day}/{month}/{year}'.format(
                    day = final_payment_day,
                    month = month_current,
                    year = payment_year,
                ),
                'basic_salary': basic_salary,
                'off_day_compensation': off_day_compensation,
                'salary_per_month': basic_salary + off_day_compensation,
                'salary_received': (
                    basic_salary + off_day_compensation - loan_repaid
                ),
                'loan_repaid': loan_repaid
            }
        
        return context

class PdfFileView(
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
