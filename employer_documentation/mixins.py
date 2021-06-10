# Python
import base64
import calendar
import datetime
from decimal import Decimal, ROUND_HALF_UP

# Django
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

# 3rd party
from weasyprint import HTML, CSS

# From our apps
from . import models, constants
from onlinemaid.constants import (
    AG_OWNERS,
    AG_ADMINS,
    AG_MANAGERS,
    AG_SALES,
)
from onlinemaid.helper_functions import intervening_weekdays
from accounts.models import User
from maid.constants import country_language

# Start of mixins
class CheckEmployerDocRelationshipsMixin(UserPassesTestMixin):
    def test_func(self):
        if self.employer_doc_obj:
            if self.object.employer.pk==self.kwargs.get('level_0_pk'):
                return True
            else:
                return False
        elif self.employer_subdoc_obj:
            if (
                self.object.employer_doc.employer.pk==self.kwargs.get(
                    'level_0_pk')
                and
                self.object.employer_doc.pk==self.kwargs.get(
                    'level_1_pk')
            ):
                return True
            else:
                return False
        else:
            return False

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse_lazy('home'))

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
                return HttpResponseRedirect(reverse_lazy('home'))
            # If successfully assigned current user's agency group to
            # agency_user_group atribute, return True so this method can also
            # serve as a validation that current user has agency role.
            return True
            
        else:
            return HttpResponseRedirect(reverse_lazy('home'))

    # Gets current user's object. Call assign_agency_user_group() first to set
    # agency_user_group attribute
    def assign_agency_user_object(self):
        if (
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_employee'
            )
            or
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_owner'
            )
        ):
            if self.agency_user_group==AG_OWNERS:
                self.agency_user_obj = self.request.user.agency_owner
            else:
                self.agency_user_obj = self.request.user.agency_employee

        else:
            return HttpResponseRedirect(reverse_lazy('home'))

    # Method to get object Employer, EmployerDoc, EmployerDocMaidStatus,
    # EmployerDocSig from database and assign to attribute of View object.
    def assign_ed_object(self):
        # Try to get object from database
        try:
            if not hasattr(self, 'object'): self.object = self.get_object()
        except Exception:
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            # Assign to respective attribute
            if isinstance(self.object, models.Employer):
                # level 0
                self.employer_obj = self.object
            elif (
                # level 1
                isinstance(self.object, models.EmployerDoc) or
                isinstance(self.object, models.EmployerSponsor) or
                isinstance(self.object, models.EmployerJointApplicant) or
                isinstance(self.object, models.EmployerIncome) or
                isinstance(self.object, models.EmployerHousehold)
            ):
                self.employer_doc_obj = self.object
            elif (
                # level 2
                isinstance(self.object, models.DocServiceFeeSchedule) or
                isinstance(self.object, models.DocServAgmtEmpCtr) or
                isinstance(self.object, models.DocSafetyAgreement) or
                isinstance(self.object, models.DocUpload) or
                isinstance(self.object, models.EmployerDocMaidStatus) or
                isinstance(self.object, models.EmployerDocSig) or
                isinstance(self.object, models.JobOrder) or
                isinstance(self.object, models.ArchivedDoc) or
                isinstance(self.object, models.EmployerPaymentTransaction)
            ):
                self.employer_subdoc_obj = self.object

    # Method to check object's agency is same as current user's agency
    def check_object_belongs_to_agency(self):
        '''
        return 1 if check FAILED
        return 0 if check PASSES
        '''
        if self.agency_user_obj:
            if (
                self.employer_obj and
                self.employer_obj.agency_employee.agency
                ==self.agency_user_obj.agency
            ):
                return 0
            elif (
                self.employer_doc_obj and
                self.employer_doc_obj.employer.agency_employee.agency
                ==self.agency_user_obj.agency
            ):
                return 0
            elif (
                self.employer_subdoc_obj and
                self.employer_subdoc_obj.employer_doc.employer
                .agency_employee.agency
                ==self.agency_user_obj.agency
            ):
                return 0
            else:
                return 1
        else:
            return 1

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('home'))
        
        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()
        
        if self.agency_user_group and self.agency_user_obj:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('home'))

class CheckAgencyEmployeePermissionsMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('home'))
        
        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()

        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_ed_object()

        # Check test object's agency is same as current user's agency
        if self.check_object_belongs_to_agency():
            return HttpResponseRedirect(reverse_lazy('home'))

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
            return HttpResponseRedirect(reverse_lazy('home'))

class CheckUserIsAgencyOwnerMixin(LoginByAgencyUserGroupRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('home'))

        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()
        
        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_ed_object()
        
        # Check test object's agency is same as current user's agency
        if self.check_object_belongs_to_agency():
            return HttpResponseRedirect(reverse_lazy('home'))

        # Check if current user is agency owner
        if self.agency_user_group==AG_OWNERS:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('home'))

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
    use_repayment_table = False

    def get_context_data(self, **kwargs):
        version_explainer_text = 'This document version supersedes all previous versions with the same Case #, if any.'
        context = super().get_context_data()

        def get_preferred_language():
            # MoM Safety Agreements are available in different languages.
            # Relevant language template snippet is selected based on FDW's
            # country of origin.
            return country_language.get(context['object'].fdw.country_of_origin, 'ENG')

        if isinstance(self.object, models.EmployerDoc):
            # Document version number formatting
            context['object'].version = f'[{self.object.get_version()}] - {version_explainer_text}'

            preferred_language = get_preferred_language()
            for i in range(1,4):
                context['lang_snippet_0'+str(i)] = f'employer_documentation/pdf/safety_agreement_snippets/{preferred_language}_snippet_0{str(i)}.html'

        return context

    def generate_pdf_response(self, request, context):
        # Render PDF
        html_template = render_to_string(self.template_name, context)
        pdf_file = HTML(
            string=html_template,
            base_url=request.build_absolute_uri()
            ).write_pdf(
                # Load separate CSS stylesheet from static folder
                stylesheets=[CSS(settings.STATIC_URL + 'css/pdf.css')]
                # stylesheets=[CSS('static/css/pdf.css')] ##################################################### TO BE CHANGED BEFORE PRODUCTION
            )
        response = HttpResponse(pdf_file, content_type='application/pdf')
        if self.content_disposition:
            response['Content-Disposition'] = self.content_disposition
        else:
            response['Content-Disposition'] = (
                'inline; filename=' + self.DEFAULT_DOWNLOAD_FILENAME
            )
        return response

    def generate_pdf_file(self, request, context, template_name):
        # Render PDF
        html_template = render_to_string(template_name, context)
        return HTML(
            string=html_template,
            base_url=request.build_absolute_uri()
            ).write_pdf(
                # target=self.target, # e.g. target=settings.MEDIA_ROOT + '/employer-documentation/test.pdf', # To save file in static folder
                # Load separate CSS stylesheet from static folder
                stylesheets=[CSS(settings.STATIC_URL + 'css/pdf.css')]
                # stylesheets=[CSS('static/css/pdf.css')] ##################################################### TO BE CHANGED BEFORE PRODUCTION
            )

    def calc_repayment_schedule(self):
        repayment_table = {}

        if hasattr(self.object, 'rn_casestatus_ed') and self.object.rn_casestatus_ed.fdw_work_commencement_date:
            DEPLOYMENT_DATE = self.object.rn_casestatus_ed.fdw_work_commencement_date
        else:
            DEPLOYMENT_DATE = None
            # DEPLOYMENT_DATE = datetime.date(2021, 5, 31) # FOR TESTING ONLY - TO BE DELETED ###################

        if DEPLOYMENT_DATE:
            # Initialise dates
            payment_year = DEPLOYMENT_DATE.year
            payment_month = DEPLOYMENT_DATE.month
            payment_day = min(DEPLOYMENT_DATE.day, calendar.monthrange(payment_year, payment_month)[1])

            # Initialise loan amounts
            MONTHLY_LOAN_REPAYMENT  = self.object.fdw_monthly_loan_repayment
            fdw_loan_balance = self.object.fdw_loan

            # Salary constant
            BASIC_SALARY = self.object.fdw_salary

            # Off day constants
            PER_OFF_DAY_COMPENSATION = self.object.per_off_day_compensation()
            FDW_OFF_DAYS_PER_MONTH = self.object.fdw_off_days
            OFF_DAY_OF_WEEK = int(self.object.fdw_off_day_of_week)

            for i in range(1,25):
                # Set start_date for calculation of potential_off_days_in_month
                if i==1:
                    # First salary month is inclusive of DEPLOYMENT_DATE for calculation of potential_off_days_in_month
                    start_date = datetime.date(payment_year, payment_month, payment_day)
                else:
                    # Otherwise, need to increase start_date by 1 day for calculation of potential_off_days_in_month
                    start_date = datetime.date(payment_year, payment_month, payment_day) + datetime.timedelta(days=1)

                # Set payment date
                payment_month += 1
                payment_month = 12 if payment_month%12==0 else payment_month%12
                payment_year += 1 if payment_month%12 == 1 else 0
                payment_day = min(DEPLOYMENT_DATE.day, calendar.monthrange(payment_year, payment_month)[1])

                # Calculate potential_off_days_in_month
                end_date = datetime.date(payment_year, payment_month, payment_day)
                potential_off_days_in_month = intervening_weekdays(start_date, end_date, inclusive=True, weekdays=[OFF_DAY_OF_WEEK])

                # Calculate salary and loan payments in month
                balance_off_day_compensation = PER_OFF_DAY_COMPENSATION * (potential_off_days_in_month - FDW_OFF_DAYS_PER_MONTH)
                total_salary = BASIC_SALARY + balance_off_day_compensation
                loan_repaid = min(MONTHLY_LOAN_REPAYMENT, BASIC_SALARY, fdw_loan_balance)

                # Each row of repayment table
                repayment_table[i] = {
                    'salary_date': '{day}/{month}/{year}'.format(
                        day = payment_day,
                        month = payment_month,
                        year = payment_year,
                    ),
                    'basic_salary': BASIC_SALARY,
                    'off_day_compensation': balance_off_day_compensation,
                    'total_salary': total_salary,
                    'loan_repaid': loan_repaid,
                    'salary_received': total_salary - loan_repaid,
                }

                # Update remaining loan balance
                fdw_loan_balance = fdw_loan_balance - loan_repaid if fdw_loan_balance-loan_repaid>=0 else 0

        else:
            # if work commencement date not set, then generate empty table
            for i in range(1,25):
                repayment_table[i] = {
                    'salary_date': '',
                    'basic_salary': '',
                    'off_day_compensation': '',
                    'total_salary': '',
                    'loan_repaid': '',
                    'salary_received': '',
                }
        
        return repayment_table
