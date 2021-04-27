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
    PdfArchive,
    EmployerPaymentTransaction,
    # EmployerSponsor,
    # EmployerJointApplicant,
)
from onlinemaid.constants import (
    AG_OWNERS,
    AG_ADMINS,
    AG_MANAGERS,
    AG_SALES,
)
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
            if isinstance(self.object, Employer):
                self.employer_obj = self.object
            elif isinstance(self.object, EmployerDoc):
                self.employer_doc_obj = self.object
            elif (
                isinstance(self.object, EmployerDocMaidStatus)
                or isinstance(self.object, EmployerDocSig)
                or isinstance(self.object, JobOrder)
                or isinstance(self.object, PdfArchive)
                or isinstance(self.object, EmployerPaymentTransaction)
                # or isinstance(self.object, EmployerSponsor)
                # or isinstance(self.object, EmployerJointApplicant)
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

    def generate_pdf_response(self, request, context):
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

    def generate_pdf_file(self, request, context, template_name):
        # Render PDF
        html_template = render_to_string(template_name, context)
        return HTML(
            string=html_template,
            base_url=request.build_absolute_uri()
            ).write_pdf(
                # target=self.target, # e.g. target=settings.MEDIA_ROOT + '/employer-documentation/test.pdf', # To save file in static folder
                # Load separate CSS stylesheet from static folder
                # stylesheets=[CSS(settings.STATIC_URL + 'css/pdf.css')]
                stylesheets=[CSS('static/css/pdf.css')] ##################################################### TO BE CHANGED BEFORE PRODUCTION
            )

    def calc_repayment_schedule(self):
        repayment_table = {}
        
        work_commencement_date = (
            self.object.rn_maidstatus_ed.fdw_work_commencement_date
        ) if self.object.rn_maidstatus_ed.fdw_work_commencement_date else None

        if work_commencement_date:
            payment_month = work_commencement_date.month
            payment_year = work_commencement_date.year
            placement_fee = (
                self.object.b3_agency_fee +
                self.object.b3_fdw_loan
            )
            placement_fee_per_month = round(placement_fee/6, 0)
            work_days_in_month = 26
            off_day_compensation = round(
                self.object.fdw.financial_details.salary*self.object.fdw.days_off/work_days_in_month, 0
            )
            salary_per_month = self.object.fdw.financial_details.salary + off_day_compensation
            
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

                    repayment_table[i] = {
                        'salary_date': '{day}/{month}/{year}'.format(
                            day = calendar.monthrange(
                                payment_year, month_current)[1],
                            month = month_current,
                            year = payment_year,
                        ),
                        'basic_salary': self.object.fdw.financial_details.salary,
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
                repayment_table[1] = {
                    'salary_date': '{day}/{month}/{year}'.format(
                        day = calendar.monthrange(
                            payment_year, month_current)[1],
                        month = month_current,
                        year = payment_year,
                        ),
                    'basic_salary': round(
                        self.object.fdw.financial_details.salary*first_month_days/
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

                    repayment_table[i] = {
                        'salary_date': '{day}/{month}/{year}'.format(
                            day = calendar.monthrange(
                                payment_year, month_current)[1],
                            month = month_current,
                            year = payment_year,
                        ),
                        'basic_salary': self.object.fdw.financial_details.salary,
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
                    self.object.fdw.financial_details.salary*final_payment_day/calendar.monthrange(
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
                repayment_table[25] = {
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
        
        else:
            for i in range(1,25):
                repayment_table[i] = {
                    'salary_date': '',
                    'basic_salary': '',
                    'off_day_compensation': '',
                    'salary_per_month': '',
                    'salary_received': '',
                    'loan_repaid': '',
                }
        return repayment_table

    def get_context_data(self, **kwargs):
        version_explainer_text = 'This document version supersedes all previous versions with the same case #, if any.'

        def get_preferred_language():
            from maid.constants import country_language
            # MoM Safety Agreements are available in different languages.
            # Relevant language template snippet is selected based on FDW's
            # country of origin.

            return country_language.get(context['object'].fdw.personal_details.country_of_origin, 'ENG')

        if isinstance(self.object, EmployerDoc):
            context = super().get_context_data(object=self.object)

            # Document version number formatting
            context['object'].version = f'[{self.object.get_version()}] - {version_explainer_text}'

            preferred_language = get_preferred_language()
            for i in range(1,4):
                context['lang_snippet_0'+str(i)] = f'employer_documentation/pdf/safety_agreement_snippets/{preferred_language}_snippet_0{str(i)}.html'

        elif isinstance(self.object, EmployerDocSig):
            '''
            context['object'] set as EmployerDoc object instead of
            EmployerDocSig so that same PDF templates can be re-used
            '''
            context = super().get_context_data(object=self.object.employer_doc)

            # Document version number formatting
            context['object'].version = f'[{self.object.employer_doc.get_version()}] - {version_explainer_text}'
        
            preferred_language = get_preferred_language()
            for i in range(1,4):
                context['lang_snippet_0'+str(i)] = f'employer_documentation/pdf/safety_agreement_snippets/{preferred_language}_snippet_0{str(i)}.html'

        else:
            context = super().get_context_data(object=self.object)

        return context
