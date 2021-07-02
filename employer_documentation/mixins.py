# Python
import calendar
import datetime
from decimal import Decimal, ROUND_HALF_UP

# Django
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
# from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

# 3rd party
from weasyprint import HTML, CSS

# From our apps
from . import models
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

        # Salary constant
        BASIC_SALARY = self.object.fdw_salary

        # Off day constants
        PER_OFF_DAY_COMPENSATION = self.object.per_off_day_compensation()
        FDW_OFF_DAYS_PER_MONTH = self.object.fdw_off_days
        OFF_DAY_OF_WEEK = int(self.object.fdw_off_day_of_week)

        # Initialise loan amounts
        MONTHLY_LOAN_REPAYMENT  = self.object.fdw_monthly_loan_repayment
        fdw_loan_balance = self.object.fdw_loan

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

            for i in range(1,25):
                # Set start_date for calculation of potential_off_days_in_month
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
                        day = str(payment_day).zfill(2),
                        month = str(payment_month).zfill(2),
                        year = str(payment_year).zfill(4),
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
            # if work commencement date not set, then generate table without dates
            for i in range(1,25):
                # Calculate salary and loan payments in month
                balance_off_day_compensation = PER_OFF_DAY_COMPENSATION * (4 - FDW_OFF_DAYS_PER_MONTH)
                total_salary = BASIC_SALARY + balance_off_day_compensation
                loan_repaid = min(MONTHLY_LOAN_REPAYMENT, BASIC_SALARY, fdw_loan_balance)

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
                fdw_loan_balance = fdw_loan_balance - loan_repaid if fdw_loan_balance-loan_repaid>=0 else 0
        
        return repayment_table
