import calendar
import datetime

from agency.mixins import AgencyLoginRequiredMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls.base import reverse_lazy
from maid.constants import COUNTRY_LANGUAGE_MAP
from onlinemaid.constants import AG_ADMINS, AG_MANAGERS, AG_OWNERS, AG_SALES
from onlinemaid.helper_functions import intervening_weekdays
from onlinemaid.mixins import GroupRequiredMixin
from weasyprint import CSS, HTML

from .models import EmployerDoc

# Start of mixins


class PdfHtmlViewMixin:
    DEFAULT_DOWNLOAD_FILENAME = "document.pdf"
    content_disposition = None
    use_repayment_table = False

    def get_context_data(self, **kwargs):
        # DO NOT FORMAT TO PEP8, IT WILL BREAK
        version_explainer_text = '''This document version supersedes all previous versions with the same Case #, if any.'''
        context = super().get_context_data()

        def get_preferred_language():
            # MoM Safety Agreements are available in different languages.
            # Relevant language template snippet is selected based on FDW's
            # country of origin.
            return COUNTRY_LANGUAGE_MAP.get(
                context['object'].fdw.country_of_origin,
                'ENG'
            )

        if isinstance(self.object, EmployerDoc):
            # Document version number formatting
            # DO NOT FORMAT TO PEP8, IT WILL BREAK
            context['object'].version = f'''[{self.object.get_version()}] - {version_explainer_text}'''

            preferred_language = get_preferred_language()
            # DO NOT FORMAT TO PEP8, IT WILL BREAK
            SAFETY_AGREEMENT_SNIPPETS_URI = '''pdf/safety_agreement_snippets'''
            for i in range(1, 4):
                # DO NOT FORMAT TO PEP8, IT WILL BREAK
                context['lang_snippet_0'+str(i)] = f'''{SAFETY_AGREEMENT_SNIPPETS_URI}/{preferred_language}_snippet_0{str(i)}.html'''

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
            # Load separate CSS stylesheet from static folder
            stylesheets=[CSS(settings.STATIC_URL + 'css/pdf.css')]
        )

    def calc_repayment_schedule(self):
        repayment_table = {}

        # Salary constant
        BASIC_SALARY = self.object.fdw_salary

        # Off day constants
        PER_OFF_DAY_COMPENSATION = self.object.get_per_off_day_compensation()
        FDW_OFF_DAYS_PER_MONTH = self.object.fdw_off_days
        OFF_DAY_OF_WEEK = int(self.object.fdw_off_day_of_week)

        # Initialise loan amounts
        MONTHLY_LOAN_REPAYMENT = self.object.fdw_monthly_loan_repayment
        fdw_loan_balance = self.object.fdw_loan

        if (
            hasattr(self.object, 'rn_casestatus_ed') and
            self.object.rn_casestatus_ed.fdw_work_commencement_date
        ):
            DEPLOYMENT_DATE = (
                self.object.rn_casestatus_ed.fdw_work_commencement_date
            )
        else:
            DEPLOYMENT_DATE = None

        if DEPLOYMENT_DATE:
            # Initialise dates
            payment_year = DEPLOYMENT_DATE.year
            payment_month = DEPLOYMENT_DATE.month
            payment_day = min(
                DEPLOYMENT_DATE.day,
                calendar.monthrange(
                    payment_year,
                    payment_month
                )[1]
            )

            for i in range(1, 25):
                # Set start_date for calculation of potential_off_days_in_month
                payment_date = datetime.date(
                    payment_year,
                    payment_month,
                    payment_day
                )
                start_date = payment_date + datetime.timedelta(days=1)

                # Set payment date
                payment_month += 1
                if payment_month % 12 == 0:
                    payment_month = 12
                else:
                    payment_month = payment_month % 12
                payment_year += 1 if payment_month % 12 == 1 else 0
                payment_day = min(
                    DEPLOYMENT_DATE.day,
                    calendar.monthrange(payment_year, payment_month)[1]
                )

                # Calculate potential_off_days_in_month
                end_date = datetime.date(
                    payment_year,
                    payment_month,
                    payment_day
                )
                potential_off_days_in_month = intervening_weekdays(
                    start_date, end_date,
                    inclusive=True,
                    weekdays=[OFF_DAY_OF_WEEK]
                )

                # Calculate salary and loan payments in month
                fdw_off_days_remaining = (
                    potential_off_days_in_month - FDW_OFF_DAYS_PER_MONTH
                )
                balance_off_day_compensation = (
                    PER_OFF_DAY_COMPENSATION * fdw_off_days_remaining
                )
                total_salary = BASIC_SALARY + balance_off_day_compensation
                loan_repaid = min(
                    MONTHLY_LOAN_REPAYMENT,
                    BASIC_SALARY,
                    fdw_loan_balance
                )

                # Each row of repayment table
                repayment_table[i] = {
                    'salary_date': '{day}/{month}/{year}'.format(
                        day=str(payment_day).zfill(2),
                        month=str(payment_month).zfill(2),
                        year=str(payment_year).zfill(4),
                    ),
                    'basic_salary': BASIC_SALARY,
                    'off_day_compensation': balance_off_day_compensation,
                    'total_salary': total_salary,
                    'loan_repaid': loan_repaid,
                    'salary_received': total_salary - loan_repaid,
                }

                # Update remaining loan balance
                if fdw_loan_balance - loan_repaid >= 0:
                    fdw_loan_balance = fdw_loan_balance - loan_repaid
                else:
                    fdw_loan_balance = 0

        else:
            # if work commencement date not set, then generate table without
            # dates
            for i in range(1, 25):
                # Calculate salary and loan payments in month
                fdw_off_days_remaining = 4 - FDW_OFF_DAYS_PER_MONTH
                balance_off_day_compensation = (
                    PER_OFF_DAY_COMPENSATION * fdw_off_days_remaining
                )
                total_salary = BASIC_SALARY + balance_off_day_compensation
                loan_repaid = min(
                    MONTHLY_LOAN_REPAYMENT,
                    BASIC_SALARY,
                    fdw_loan_balance
                )

                # Each row of repayment table
                repayment_table[i] = {
                    'salary_date': '',
                    'basic_salary': BASIC_SALARY,
                    'off_day_compensation': balance_off_day_compensation,
                    'total_salary': total_salary,
                    'loan_repaid': loan_repaid,
                    'salary_received': total_salary - loan_repaid,
                }

                # Update remaining loan balance
                if fdw_loan_balance - loan_repaid >= 0:
                    fdw_loan_balance = fdw_loan_balance - loan_repaid
                else:
                    fdw_loan_balance = 0
        return repayment_table


class GetObjFromSigSlugMixin:
    def get_object_from_slug(self, slug):
        obj = None
        try:
            if self.stakeholder == 'employer_1':
                obj = self.model.objects.get(
                    sigslug_employer_1=slug
                )
            elif self.stakeholder == 'employer_spouse':
                obj = self.model.objects.get(
                    sigslug_employer_spouse=slug
                )
            elif self.stakeholder == 'sponsor_1':
                obj = self.model.objects.get(
                    sigslug_sponsor_1=slug
                )
            elif self.stakeholder == 'sponsor_2':
                obj = self.model.objects.get(
                    sigslug_sponsor_2=slug
                )
            elif self.stakeholder == 'joint_applicant':
                obj = self.model.objects.get(
                    sigslug_joint_applicant=slug
                )
        except self.model.DoesNotExist:
            pass
        finally:
            return obj


class EmployerRequiredMixin(GroupRequiredMixin):
    group_required = u"Employers"
    login_url = reverse_lazy('sign_in')
    permission_denied_message = '''You are required to login to perform this
                                action'''


class EmployerDocAccessMixin(EmployerRequiredMixin):
    permission_denied_message = '''Access permission denied'''

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        access_granted = False

        # If URL has pk, then check user access permissions
        if self.kwargs.get(self.pk_url_kwarg):
            # Set agency user object
            try:
                test_user = get_user_model().objects.get(
                    pk=request.user.pk
                )
            except Exception:
                access_granted = False
            else:

                # Set employer object
                test_obj = self.get_object()
                required_user = test_obj.employer.potential_employer.user
                access_granted = test_user == required_user

        # If URL does not have pk, then fall back to inherited dispatch handler
        else:
            access_granted = True

        if access_granted:
            return handler
        else:
            return self.handle_no_permission(request)


class AgencyAccessToEmployerDocAppMixin(AgencyLoginRequiredMixin):
    permission_denied_message = '''Access permission denied'''

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        access_granted = False

        # If URL has pk, then check user access permissions
        if self.kwargs.get(self.pk_url_kwarg):
            # Set agency user object
            test_user = get_user_model().objects.get(pk=request.user.pk)
            if hasattr(test_user, 'agency_owner'):
                agency_user_obj = test_user.agency_owner
            elif hasattr(test_user, 'agency_employee'):
                agency_user_obj = test_user.agency_employee
            else:
                agency_user_obj = None

            # Set employer object
            employer_obj = None
            test_obj = self.get_object() if agency_user_obj else None
            if test_obj:
                if hasattr(test_obj, 'applicant_type'):
                    employer_obj = test_obj
                elif hasattr(test_obj, 'employer'):
                    employer_obj = test_obj.employer
                elif hasattr(test_obj, 'employer_doc'):
                    employer_obj = test_obj.employer_doc.employer

            # Check agency user permissions vs employer object
            if (
                employer_obj and
                employer_obj.agency_employee.agency == agency_user_obj.agency
            ):
                if self.authority == AG_OWNERS:
                    access_granted = True
                elif self.authority == AG_ADMINS:
                    access_granted = True  # TODO: Handle no permission
                elif self.authority == AG_MANAGERS:
                    employer_agent = employer_obj.agency_employee
                    if employer_agent.branch == agency_user_obj.branch:
                        access_granted = True
                elif self.authority == AG_SALES:
                    if employer_obj.agency_employee == agency_user_obj:
                        access_granted = True

        # If URL does not have pk, then fall back to inherited dispatch handler
        else:
            access_granted = True

        if access_granted:
            return handler
        else:
            return self.handle_no_permission(request)


class OwnerAccessToEmployerDocAppMixin(AgencyAccessToEmployerDocAppMixin):
    permission_denied_message = '''Access permission denied'''

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        if self.authority == AG_OWNERS:
            return handler
        else:
            return self.handle_no_permission(request)
