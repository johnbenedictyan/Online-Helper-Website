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
    EmployerForm,
#     EmployerBaseAgentForm,
#     EmployerDocBaseForm,
#     EmployerExtraInfoForm,
#     EmployerDocJobOrderForm,
#     EmployerDocServiceFeeBaseForm,
#     EmployerDocServiceAgreementForm,
#     EmployerDocEmploymentContractForm,
#     SignatureEmployerForm,
#     SignatureSpouseForm,
#     SignatureSponsorForm,
#     SignatureFdwForm,
#     SignatureAgencyStaffForm,
)
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
)
from .mixins import (
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     CheckEmployerSubDocBelongsToEmployerMixin,
    CheckAgencyEmployeePermissionsMixin,
#     CheckAgencyEmployeePermissionsEmployerExtraInfoMixin,
#     CheckAgencyEmployeePermissionsDocBaseMixin,
#     CheckAgencyEmployeePermissionsSubDocMixin,
#     CheckUserHasAgencyRoleMixin,
    CheckUserIsAgencyOwnerMixin,
    LoginByAgencyUserGroupRequiredMixin,
#     PdfViewMixin,
)
from agency.models import (
    AgencyEmployee,
    AgencyOwner
)
from accounts.models import User
from . import mixins as ed_mixins


# Start of Views

# Template Views

# Redirect Views

# List Views
class EmployerListView(
    LoginByAgencyUserGroupRequiredMixin,
    ListView
):
    model = Employer
    ordering = ['employer_name']
    # paginate_by = 10

    # Filter queryset to only show the employers that current user has necessary permission to access
    def get_queryset(self):
        # Get current user's group using LoginByAgencyUserGroupRequiredMixin's get_agency_user_group() method
        self.get_agency_user_group()

        if self.agency_user_group==ed_mixins.AG_OWNERS:
            # If agency owner, return all employers belonging to agency
            return super().get_queryset().filter(
                agency_employee__agency
                = self.request.user.agency_owner.agency
            )
        elif self.agency_user_group==ed_mixins.AG_ADMINS:
            # If agency administrator, return all employers belonging to agency
            return super().get_queryset().filter(
                agency_employee__agency
                = self.request.user.agency_employee.agency
            )
        elif self.agency_user_group==ed_mixins.AG_MANAGERS:
            # If agency manager, return all employers belonging to branch
            return super().get_queryset().filter(
                agency_employee__branch
                = self.request.user.agency_employee.branch
            )
        elif self.agency_user_group==ed_mixins.AG_SALES:
            # If agency owner, return all employers belonging to self
            return super().get_queryset().filter(
                agency_employee = self.request.user.agency_employee
            )
        else:
            return self.handle_no_permission()

# class EmployerDocBaseListView(
#     CheckAgencyEmployeePermissionsEmployerBaseMixin,
#     ListView
# ):
#     model = EmployerDocBase
#     pk_url_kwarg = 'employer_base_pk'
#     ordering = ['pk']

#     def get_queryset(self):
#         return super().get_queryset().filter(employer=self.kwargs.get(
#             self.pk_url_kwarg))

# Detail Views
class EmployerDetailView(
    CheckAgencyEmployeePermissionsMixin,
    DetailView,
):
    model = Employer
    pk_url_kwarg = 'employer_pk'

# class EmployerDocBaseDetailView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     CheckAgencyEmployeePermissionsDocBaseMixin,
#     DetailView
# ):
#     model = EmployerDocBase
#     pk_url_kwarg = 'employer_doc_base_pk'

# Create Views
class EmployerCreateView(
    LoginByAgencyUserGroupRequiredMixin,
    CreateView
):
    model = Employer
    form_class = EmployerForm
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        self.get_agency_user_group()
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

    def form_valid(self, form):
        if self.agency_user_group==ed_mixins.AG_SALES:
            form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

# class EmployerDocBaseCreateView(
#     CheckAgencyEmployeePermissionsEmployerBaseMixin,
#     CreateView
# ):
#     model = EmployerDocBase
#     form_class = EmployerDocBaseForm
#     pk_url_kwarg = 'employer_base_pk'
#     template_name = 'employer_documentation/employer-form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['agency_user_group'] = self.agency_user_group
#         return kwargs

#     def form_valid(self, form):
#         form.instance.employer = EmployerBase.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# class EmployerDocServiceAgreementCreateView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     CheckAgencyEmployeePermissionsDocBaseMixin,
#     CreateView
# ):
#     model = EmployerDocServiceAgreement
#     form_class = EmployerDocServiceAgreementForm
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/employer-form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def form_valid(self, form):
#         form.instance.employer_doc_base = EmployerDocBase.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# # Update Views
class EmployerUpdateView(
    CheckAgencyEmployeePermissionsMixin,
    UpdateView
):
    model = Employer
    form_class = EmployerForm
    pk_url_kwarg = 'employer_pk'
    success_url = reverse_lazy('employer_list_route')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['agency_user_group'] = self.agency_user_group
        return kwargs

# class EmployerBaseUpdateAgentView(
#     CheckAgencyEmployeePermissionsEmployerBaseMixin,
#     UpdateView
# ):
#     model = EmployerBase
#     form_class = EmployerBaseAgentForm
#     pk_url_kwarg = 'employer_base_pk'
#     template_name = 'employer_documentation/employer-form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def dispatch(self, request, *args, **kwargs):
#         # Call inherited dispatch() method first to perform initial
#         # permissions checks and set agency_user_group attribute.
#         super().dispatch(request, *args, **kwargs)

#         # If current user is part of sales staff group, deny access
#         if self.agency_user_group==ed_mixins.AG_SALES:
#             self.handle_no_permission()
#         else:
#             return super().dispatch(request, *args, **kwargs)

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         return kwargs

# class EmployerDocBaseUpdateView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     CheckAgencyEmployeePermissionsDocBaseMixin,
#     UpdateView
# ):
#     model = EmployerDocBase
#     form_class = EmployerDocBaseForm
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/employer-form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['agency_user_group'] = self.agency_user_group
#         return kwargs

# class EmployerDocServiceAgreementUpdateView(
#     CheckEmployerSubDocBelongsToEmployerMixin,
#     CheckAgencyEmployeePermissionsSubDocMixin,
#     UpdateView
# ):
#     model = EmployerDocServiceAgreement
#     form_class = EmployerDocServiceAgreementForm
#     pk_url_kwarg = 'employer_doc_service_agreement_pk'
#     template_name = 'employer_documentation/employer-form.html'
#     success_url = reverse_lazy('employer_base_list')

# # Delete Views
class EmployerDeleteView(CheckUserIsAgencyOwnerMixin, DeleteView):
    model = Employer
    pk_url_kwarg = 'employer_pk'
    success_url = reverse_lazy('employer_list_route')

# class EmployerDocBaseDeleteView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     CheckUserIsAgencyOwnerMixin,
#     DeleteView
# ):
#     model = EmployerDocBase
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/employerbase_confirm_delete.html'
#     success_url = reverse_lazy('employer_base_list')


# # Signature Views
# class SignatureEmployerCreateView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsDocBaseMixin,
#     CreateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureEmployerForm
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def form_valid(self, form):
#         form.instance.employer_doc_base = EmployerDocBase.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# class SignatureEmployerUpdateView(
#     CheckEmployerSubDocBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsSubDocMixin,
#     UpdateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureEmployerForm
#     pk_url_kwarg = 'docsig_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

# class SignatureSpouseCreateView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsDocBaseMixin,
#     CreateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureSpouseForm
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def form_valid(self, form):
#         form.instance.employer_doc_base = EmployerDocBase.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# class SignatureSpouseUpdateView(
#     CheckEmployerSubDocBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsSubDocMixin,
#     UpdateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureSpouseForm
#     pk_url_kwarg = 'docsig_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

# class SignatureSponsorCreateView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsDocBaseMixin,
#     CreateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureSponsorForm
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def form_valid(self, form):
#         form.instance.employer_doc_base = EmployerDocBase.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# class SignatureSponsorUpdateView(
#     CheckEmployerSubDocBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsSubDocMixin,
#     UpdateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureSponsorForm
#     pk_url_kwarg = 'docsig_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

# class SignatureFdwCreateView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsDocBaseMixin,
#     CreateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureFdwForm
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def form_valid(self, form):
#         form.instance.employer_doc_base = EmployerDocBase.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# class SignatureFdwUpdateView(
#     CheckEmployerSubDocBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsSubDocMixin,
#     UpdateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureFdwForm
#     pk_url_kwarg = 'docsig_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

# class SignatureAgencyStaffCreateView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     CheckAgencyEmployeePermissionsDocBaseMixin,
#     CreateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureAgencyStaffForm
#     pk_url_kwarg = 'employer_doc_base_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')

#     def form_valid(self, form):
#         form.instance.employer_doc_base = EmployerDocBase.objects.get(
#             pk = self.kwargs.get(self.pk_url_kwarg)
#         )
#         return super().form_valid(form)

# class SignatureAgencyStaffUpdateView(
#     CheckEmployerSubDocBelongsToEmployerMixin,
#     CheckAgencyEmployeePermissionsSubDocMixin,
#     UpdateView
# ):
#     model = EmployerDocSig
#     form_class = SignatureAgencyStaffForm
#     pk_url_kwarg = 'docsig_pk'
#     template_name = 'employer_documentation/signature_form.html'
#     success_url = reverse_lazy('employer_base_list')


# # PDF Views
# class PdfEmployerAgreementView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsSubDocMixin,
#     PdfViewMixin,
#     DetailView
# ):
#     model = EmployerDocBase
#     pk_url_kwarg = 'employer_doc_base_pk'

# import calendar
# from django.utils import timezone
# class PdfRepaymentScheduleView(
#     CheckEmployerDocBaseBelongsToEmployerMixin,
#     # CheckAgencyEmployeePermissionsSubDocMixin,
#     PdfViewMixin,
#     DetailView
# ):
#     model = EmployerDocBase
#     pk_url_kwarg = 'employer_doc_base_pk'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['repayment_table'] = {}
#         today = timezone.now()

#         payment_month = today.month
#         payment_year = today.year
#         placement_fee = 3000
#         placement_fee_per_month = round(placement_fee/6, 0)
#         work_days_in_month = 26
#         off_day_compensation = round(
#             self.object.fdw.salary/work_days_in_month, 0
#         )
#         salary_per_month = self.object.fdw.salary + off_day_compensation
        
#         if (
#             self.object.rn_employerdocmaidstatus.fdw_work_commencement_date
#             .day==1
#         ):
#             # If work start date is 1st of month, then payment does not need
#             # to be pro-rated.
#             for i in range(1,25):
#                 month_current = (
#                     12 if payment_month%12==0 else payment_month%12
#                 )
#                 loan_repaid = min(
#                     placement_fee,
#                     placement_fee_per_month,
#                     salary_per_month
#                 )

#                 context['repayment_table'][i] = {
#                     'salary_date': '{day}/{month}/{year}'.format(
#                         day = calendar.monthrange(
#                             payment_year, month_current)[1],
#                         month = month_current,
#                         year = payment_year,
#                     ),
#                     'basic_salary': self.object.fdw.salary,
#                     'off_day_compensation': off_day_compensation,
#                     'salary_per_month': salary_per_month,
#                     'salary_received': salary_per_month-loan_repaid,
#                     'loan_repaid': loan_repaid
#                 }
#                 placement_fee = (
#                     placement_fee-loan_repaid
#                     if placement_fee-loan_repaid>=0
#                     else 0
#                 )
#                 payment_month += 1
#                 if payment_month%12 == 1:
#                     payment_year += 1

#         else:
#             # Pro-rated payments
#             month_current = (
#                 12 if payment_month%12==0 else payment_month%12
#             )
#             first_month_days = (
#                 calendar.monthrange(
#                     payment_year, month_current)[1]
#                 - self.object.rn_employerdocmaidstatus
#                 .fdw_work_commencement_date.day + 1
#             )
#             first_month_salary = round(salary_per_month*first_month_days/
#                 calendar.monthrange(payment_year, month_current)[1], 0)
#             loan_repaid = min(
#                 placement_fee,
#                 placement_fee_per_month,
#                 round(salary_per_month*first_month_days/calendar.monthrange(
#                     payment_year, month_current)[1], 0)
#             )

#             # 1st month pro-rated
#             context['repayment_table'][1] = {
#                 'salary_date': '{day}/{month}/{year}'.format(
#                     day = calendar.monthrange(
#                         payment_year, month_current)[1],
#                     month = month_current,
#                     year = payment_year,
#                     ),
#                 'basic_salary': round(
#                     self.object.fdw.salary*first_month_days/
#                     calendar.monthrange(
#                         payment_year, month_current)[1], 0
#                 ),
#                 'off_day_compensation': round(
#                     off_day_compensation*first_month_days/
#                     calendar.monthrange(
#                         payment_year, month_current)[1], 0
#                 ),
#                 'salary_per_month': first_month_salary,
#                 'salary_received': first_month_salary - loan_repaid,
#                 'loan_repaid': loan_repaid
#             }
#             placement_fee = (
#                 placement_fee-loan_repaid
#                 if placement_fee-loan_repaid>=0
#                 else 0
#             )
#             payment_month += 1
#             if payment_month%12 == 1:
#                 payment_year += 1

#             # 2nd-23rd months of full month payments
#             for i in range(2,25):
#                 month_current = (
#                     12 if payment_month%12==0 else payment_month%12
#                 )
#                 loan_repaid = min(
#                     placement_fee,
#                     placement_fee_per_month,
#                     salary_per_month
#                 )

#                 context['repayment_table'][i] = {
#                     'salary_date': '{day}/{month}/{year}'.format(
#                         day = calendar.monthrange(
#                             payment_year, month_current)[1],
#                         month = month_current,
#                         year = payment_year,
#                     ),
#                     'basic_salary': self.object.fdw.salary,
#                     'off_day_compensation': off_day_compensation,
#                     'salary_per_month': salary_per_month,
#                     'salary_received': salary_per_month-loan_repaid,
#                     'loan_repaid': loan_repaid
#                 }
#                 placement_fee = (
#                     placement_fee-loan_repaid
#                     if placement_fee-loan_repaid>=0
#                     else 0
#                 )
#                 payment_month += 1
#                 if payment_month%12 == 1:
#                     payment_year += 1

#             # 25th month pro-rated
#             final_payment_day = (
#                 self.object.rn_employerdocmaidstatus
#                 .fdw_work_commencement_date.day - 1
#             )
#             basic_salary = round(
#                 self.object.fdw.salary*final_payment_day/calendar.monthrange(
#                     payment_year, month_current)[1]
#             )
#             off_day_compensation = round(
#                 off_day_compensation*final_payment_day/calendar.monthrange(
#                     payment_year, month_current)[1]
#             )
#             context['repayment_table'][25] = {
#                 'salary_date': '{day}/{month}/{year}'.format(
#                     day = final_payment_day,
#                     month = month_current,
#                     year = payment_year,
#                 ),
#                 'basic_salary': basic_salary,
#                 'off_day_compensation': off_day_compensation,
#                 'salary_per_month': basic_salary + off_day_compensation,
#                 'salary_received': (
#                     basic_salary + off_day_compensation - loan_repaid
#                 ),
#                 'loan_repaid': loan_repaid
#             }
        
#         return context
