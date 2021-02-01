# Python
import base64
import calendar

# Django
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

# 3rd party
from weasyprint import HTML, CSS

# From our apps
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
    JobOrder,
)
from onlinemaid.constants import (
    AG_OWNERS,
    AG_ADMINS,
    AG_MANAGERS,
    AG_SALES,
)
from onlinemaid.helper_functions import decrypt_string
from accounts.models import User


# Start of mixins
class CheckEmployerDocRelationshipsMixin(UserPassesTestMixin):
    def test_func(self):
        if self.employer_doc_obj:
            if self.object.employer.pk==self.kwargs.get('employer_pk'):
                return True
            else:
                return False
        elif self.employer_subdoc_obj:
            if (
                self.object.employer_doc.employer.pk==self.kwargs.get(
                    'employer_pk')
                and
                self.object.employer_doc.pk==self.kwargs.get(
                    'employerdoc_pk')
            ):
                return True
            else:
                return False
        else:
            return False

class LoginByAgencyUserGroupRequiredMixin(LoginRequiredMixin):
    '''
    This is a helper mixin that does not override any inherited methods or
    attributes. Use to add additional functionality to LoginRequiredMixin.
    '''
    agency_user_group = None
    agency_user_obj = None
    employer_obj = None
    employer_doc_obj = None
    employer_subdoc_obj = None

    # Gets current user's assigned agency group. Needs to be called manually.
    def assign_agency_user_group(self):
        # First check if current user is agency_employee or agency_owner.
        # If neither, then permission check failed, no further checks needed.
        if (
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_employee'
            )
            or
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_owner'
            )
        ):
            # Assign current user's agency group to agency_user_group atribute
            if self.request.user.groups.filter(name=AG_OWNERS).exists():
                self.agency_user_group = AG_OWNERS
            elif (
                self.request.user.groups.filter(name=AG_ADMINS)
                .exists()
            ):
                self.agency_user_group = AG_ADMINS
            elif (
                self.request.user.groups.filter(name=AG_MANAGERS).exists()
            ):
                self.agency_user_group = AG_MANAGERS
            elif (
                self.request.user.groups.filter(name=AG_SALES)
                .exists()
            ):
                self.agency_user_group = AG_SALES
            else:
                return self.handle_no_permission()
            # If successfully assigned current user's agency group to
            # agency_user_group atribute, return True so this method can also
            # serve as a validation that current user has agency role.
            return True
            
        else:
            return self.handle_no_permission()

    # Gets current user's object. Call assign_agency_user_group() first to set
    # agency_user_group attribute
    def assign_agency_user_object(self):
        if self.agency_user_group==AG_OWNERS:
            self.agency_user_obj = self.request.user.agency_owner
        else:
            self.agency_user_obj = self.request.user.agency_employee

    # Method to get object Employer, EmployerDoc, EmployerDocMaidStatus,
    # EmployerDocSig from database and assign to attribute of View object.
    def assign_ed_object(self):
        # Try to get object from database
        try:
            if not hasattr(self, 'object'): self.object = self.get_object()
        except:
            return self.handle_no_permission()
        else:
            # Assign to respective attribute
            if isinstance(self.object, Employer):
                self.employer_obj = self.object
            elif isinstance(self.object, EmployerDoc):
                self.employer_doc_obj = self.object
            elif (
                isinstance(self.object, EmployerDocMaidStatus)
                or isinstance(self.object, EmployerDocSig)
                or isinstance(self.object, JobOrder)
            ):
                self.employer_subdoc_obj = self.object

    # Method to check object's agency is same as current user's agency
    def check_object_belongs_to_agency(self):
        if (
            self.employer_obj and
            not self.employer_obj.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()
        elif (
            self.employer_doc_obj and
            not self.employer_doc_obj.employer.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()
        elif (
            self.employer_subdoc_obj and
            not self.employer_subdoc_obj.employer_doc.employer
            .agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()
        return super().dispatch(request, *args, **kwargs)

class CheckAgencyEmployeePermissionsMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()

        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_ed_object()

        # Check test object's agency is same as current user's agency
        self.check_object_belongs_to_agency()

        # Check user belongs to required group to access view
        if (
            self.agency_user_group==AG_OWNERS
            or
            self.agency_user_group==AG_ADMINS
            or (
                self.agency_user_group==AG_MANAGERS and
                self.employer_obj and
                self.agency_user_obj.branch==
                self.employer_obj.agency_employee.branch
            )
            or (
                self.agency_user_group==AG_MANAGERS and
                self.employer_doc_obj and
                self.agency_user_obj.branch==
                self.employer_doc_obj.employer.agency_employee.branch
            )
            or (
                self.agency_user_group==AG_MANAGERS and
                self.employer_subdoc_obj and
                self.agency_user_obj.branch==
                self.employer_subdoc_obj.employer_doc.employer.agency_employee
                .branch
            )
            or (
                self.employer_obj and
                self.employer_obj.agency_employee==self.agency_user_obj
            )
            or (
                self.employer_doc_obj and
                self.employer_doc_obj.employer.agency_employee
                ==self.agency_user_obj
            )
            or (
                self.employer_subdoc_obj and
                self.employer_subdoc_obj.employer_doc.employer.agency_employee
                ==self.agency_user_obj
            )
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckUserIsAgencyOwnerMixin(LoginByAgencyUserGroupRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()
        
        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_ed_object()
        
        # Check test object's agency is same as current user's agency
        self.check_object_belongs_to_agency()

        # Check if current user is agency owner
        if self.agency_user_group==AG_OWNERS:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

# Signature Mixin
class CheckSignatureSessionTokenMixin(UserPassesTestMixin):
    def test_func(self):
        if (
            self.request.session.get('signature_token') ==
            getattr(self.get_object(), self.token_field_name)
        ):
            return True
        else:
            return False

# PDF Mixin
class PdfHtmlViewMixin:
    DEFAULT_DOWNLOAD_FILENAME = "document.pdf"
    content_disposition = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if isinstance(self.object, EmployerDoc):
            # If FDW work commencement date is empty, then redirect to update
            if not self.object.fdw_work_commencement_date:
                return HttpResponseRedirect(
                    reverse('employerdoc_agreement_date_update_route', kwargs={
                        'employer_pk': self.object.employer.pk,
                        'employerdoc_pk': self.object.pk,
                    }))
            # Get context data
            context = self.get_context_data(object=self.object)
        
        elif isinstance(self.object, EmployerDocSig):
            # Get context data
            context = self.get_context_data(object=self.object.employer_doc)
        else:
            return HttpResponseRedirect(
                reverse('home'))

        # Render PDF
        html_template = render_to_string(self.template_name, context)
        pdf_file = HTML(
            string=html_template,
            base_url=request.build_absolute_uri()
            ).write_pdf(
                # Load separate CSS stylesheet from static folder
                # stylesheets=[CSS(settings.STATIC_URL + 'css/pdf.css')]
                stylesheets=[CSS('static/css/pdf.css')] ##################################################### TO BE CHANGED BEFORE PRODUCTION
            )
        response = HttpResponse(pdf_file, content_type='application/pdf')
        if self.content_disposition:
            response['Content-Disposition'] = self.content_disposition
        else:
            response['Content-Disposition'] = (
                'inline; filename=' + self.DEFAULT_DOWNLOAD_FILENAME
            )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if isinstance(self.object, EmployerDoc):
            try:
                context['object'].employer.employer_nric = decrypt_string(
                    self.object.employer.employer_nric,
                    settings.ENCRYPTION_KEY,
                    self.object.employer.nonce,
                    self.object.employer.tag
                )
            except (ValueError, KeyError):
                print("Incorrect decryption")
                context['object'].employer.employer_nric = ''
        elif isinstance(self.object, EmployerDocSig):
            try:
                context['object'].employer_doc.employer.employer_nric = decrypt_string(
                    self.object.employer_doc.employer.employer_nric,
                    settings.ENCRYPTION_KEY,
                    self.object.employer_doc.employer.nonce,
                    self.object.employer_doc.employer.tag
                )
            except (ValueError, KeyError):
                print("Incorrect decryption")
                context['object'].employer.employer_nric = ''
        return context

class RepaymentScheduleMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repayment_table'] = {}
        
        work_commencement_date = (
            self.object.fdw_work_commencement_date
        )

        payment_month = work_commencement_date.month
        payment_year = work_commencement_date.year
        placement_fee = (
            self.object.fdw.agency_fee_amount +
            self.object.fdw.personal_loan_amount
        )
        placement_fee_per_month = round(placement_fee/6, 0)
        work_days_in_month = 26
        off_day_compensation = round(
            self.object.fdw.salary*self.object.fdw.days_off/work_days_in_month, 0
        )
        salary_per_month = self.object.fdw.salary + off_day_compensation
        
        # If work start date is 1st of month, then payment does not need to be pro-rated
        if work_commencement_date and work_commencement_date.day==1:
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

        # Pro-rated payments
        if work_commencement_date and not work_commencement_date.day==1:
            month_current = (
                12 if payment_month%12==0 else payment_month%12
            )
            first_month_days = (
                calendar.monthrange(
                    payment_year,
                    month_current)[1] - work_commencement_date.day + 1
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
                work_commencement_date.day-1,
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
