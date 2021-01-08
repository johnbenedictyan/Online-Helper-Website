# Imports from python
import os
import uuid

# Imports from django
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator

# Imports from other apps
from onlinemaid.constants import TrueFalseChoices
from agency.models import AgencyEmployee
from maid.models import Maid

# Utiliy Classes and Functions
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, filename, max_length=100):
        if self.exists(filename):
            os.remove(os.path.join(self.location, filename))
        return filename

def generate_joborder_path(instance, filename):
    ext = 'pdf'
    
    # Generate custom filename
    if instance.slug:
        filename = '{}.{}'.format(instance.slug, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(
        'employer-documentation/job-orders/',
        filename
    )


# Start of Models

# Employer e-Documentation Models
class Employer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    agency_employee = models.ForeignKey(
        AgencyEmployee,
        verbose_name=_('Assigned Agent / Salesperson'),
        on_delete=models.RESTRICT
    )
    employer_name = models.CharField(
        verbose_name=_('Employer Name'),
        max_length=40
    )
    employer_email = models.EmailField(verbose_name=_('Email Address'))
    employer_mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[8-9][0-9]{7}$', # Singapore mobile numbers
                # regex='^[8-9][0-9]{7}[0-9]*$',
                message=_('Please enter a valid contact number')
            )
        ]
    )
    employer_nric = models.CharField(
        verbose_name=_('NRIC / FIN'),
        max_length=20
    )
    employer_address_1 = models.CharField(
        verbose_name=_('Street Address'),
        max_length=100,
    )

    employer_address_2 = models.CharField(
        verbose_name=_('Unit Number'),
        max_length=50,
    )

    employer_post_code = models.CharField(
        verbose_name=_('Post Code'),
        max_length=25,
    )


class EmployerDoc(models.Model):
    DAY_CHOICES = [
        (0, "0 days"),
        (1, "1 day"),
        (2, "2 days"),
        (3, "3 days"),
        (4, "4 days"),
        (5, "5 days"),
        (6, "6 days"),
        (7, "7 days"),
        (8, "8 days"),
        (9, "9 days"),
        (10, "10 days"),
        (11, "11 days"),
        (12, "12 days"),
        (13, "13 days"),
        (14, "14 days"),
        (15, "15 days"),
        (16, "16 days"),
        (17, "17 days"),
        (18, "18 days"),
        (19, "19 days"),
        (20, "20 days"),
        (21, "21 days"),
        (22, "22 days"),
        (23, "23 days"),
        (24, "24 days"),
        (25, "25 days"),
        (26, "26 days"),
        (27, "27 days"),
        (28, "28 days"),
    ]

    WEEK_CHOICES = [
        (0, "0 weeks"),
        (1, "1 week"),
        (2, "2 weeks"),
        (3, "3 weeks"),
        (4, "4 weeks"),
    ]

    MONTH_CHOICES = [
        (0, "0 months"),
        (1, "1 month"),
        (2, "2 months"),
        (3, "3 months"),
        (4, "4 months"),
        (5, "5 months"),
        (6, "6 months"),
        (7, "7 months"),
        (8, "8 months"),
        (9, "9 months"),
        (10, "10 months"),
        (11, "11 months"),
        (12, "12 months"),
        (13, "13 months"),
        (14, "14 months"),
        (15, "15 months"),
        (16, "16 months"),
        (17, "17 months"),
        (18, "18 months"),
        (19, "19 months"),
        (20, "20 months"),
        (21, "21 months"),
        (22, "22 months"),
        (23, "23 months"),
        (24, "24 months"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    case_ref_no = models.CharField(
        verbose_name=_("Case Reference Number"),
        max_length=20,
        unique=True
    )
    employer = models.ForeignKey(
        Employer,
        on_delete=models.RESTRICT,
        related_name='rn_ed_employer'
    )
    fdw = models.ForeignKey(
        Maid,
        verbose_name=_("Foreign Domestic Worker (FDW)"),
        on_delete=models.RESTRICT
    )
    spouse_required = models.BooleanField(
        verbose_name=_("Is spouse requried?"),
        choices=TrueFalseChoices(
            'Yes, spouse required',
            'No, spouse not required'
        ),
    )
    sponsor_required = models.BooleanField(
        verbose_name=_("Is sponsor requried?"),
        choices=TrueFalseChoices(
            'Yes, sponsor required',
            'No, sponsor not required'
        ),
    )

    # Service Fee Schedule
    b1_service_fee = models.PositiveIntegerField(
        # cents
        verbose_name=_("Service Fee"),
    )
    b2a_work_permit_application_collection = models.PositiveIntegerField(
        # cents
        verbose_name=_("Application / Collection of Work Permit"),
    )
    b2b_medical_examination_fee = models.PositiveIntegerField(
        # cents
        verbose_name=_("Medical Examination Fee"),
    )
    b2c_security_bond_accident_insurance = models.PositiveIntegerField(
        # cents
        verbose_name=_("Security Bond and Personal Accident Insurance"),
    )
    b2d_indemnity_policy_reimbursement = models.PositiveIntegerField(
        # cents
        verbose_name=_("Reimbursement of Indemnity Policy"),
    )
    b2e_home_service = models.PositiveIntegerField(
        # cents
        verbose_name=_("Home Service"),
    )
    b2f_counselling = models.PositiveIntegerField(
        # cents
        verbose_name=_("Each Counselling Session"),
    )
    b2g_sip = models.PositiveIntegerField(
        # cents
        verbose_name=_("Settling-In-Programme (SIP)"),
    )
    b2h_replacement_months = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("Cost for replacement within __ month(s)"),
        choices=MONTH_CHOICES
    )
    b2h_replacement_cost = models.PositiveIntegerField(
        # cents
        verbose_name=_("Cost for replacement"),
    )
    b2i_work_permit_renewal = models.PositiveIntegerField(
        # cents
        verbose_name=_("Renewal of Work Permit"),
    )
    b2j1_other_services_description = models.CharField(
        verbose_name=_("Other services provided (i)"),
        max_length=40,
        blank=True,
        null=True
    )
    b2j1_other_services_fee = models.PositiveIntegerField(
        # cents
        verbose_name=_("Other services fee (i)"),
        blank=True,
        null=True
    )
    b2j2_other_services_description = models.CharField(
        verbose_name=_("Other services provided (ii)"),
        max_length=40,
        blank=True,
        null=True
    )
    b2j2_other_services_fee = models.PositiveIntegerField(
        # cents
        verbose_name=_("Other services fee (ii)"),
        blank=True,
        null=True
    )
    b2j3_other_services_description = models.CharField(
        verbose_name=_("Other services provided (iii)"),
        max_length=40,
        blank=True,
        null=True
    )
    b2j3_other_services_fee = models.PositiveIntegerField(
        # cents
        verbose_name=_("Other services fee (iii)"),
        blank=True,
        null=True
    )
    ca_deposit = models.PositiveIntegerField(
        # cents
        verbose_name=_("Deposit - upon confirmation of FDW")
    )

    # If FDW is replacement, then additional fields
    fdw_is_replacement = models.BooleanField(
        verbose_name=_("Is this FDW a replacement?"),
        choices=TrueFalseChoices(
            'Yes, replacement',
            'No, not replacement'
        ),
    )
    fdw_replaced = models.ForeignKey(
        Maid,
        verbose_name=_("FDW Replaced* (required if FDW is replacement)"),
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name='rn_ed_fdwreplaced'
    )
    b4_loan_transferred = models.PositiveIntegerField(
        # cents
        verbose_name=_("Loan Transferred* (required if FDW is replacement)"),
        blank=True,
        null=True,
    )

    # Service Agreement
    c1_3_handover_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("handover FDW to Employer within __ day(s)"),
        choices=DAY_CHOICES
    )
    c3_2_no_replacement_criteria_1 = models.CharField(
        verbose_name=_("No need to provide Employer with replacement FDW \
            if any of following circumstances (i)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_2 = models.CharField(
        verbose_name=_("No need to provide Employer with replacement FDW \
            if any of following circumstances (ii)"),
        max_length=100
    )
    c3_2_no_replacement_criteria_3 = models.CharField(
        verbose_name=_("No need to provide Employer with replacement FDW \
            if any of following circumstances (iii)"),
        max_length=100
    )
    c3_4_no_replacement_refund = models.PositiveIntegerField(
        # cents
        verbose_name=_("Refund amount if no replacement pursuant to Clause \
            3.1"),
    )
    c4_1_number_of_replacements = models.PositiveSmallIntegerField(
        verbose_name=_("Number of replacement FDWs that Employer is entitled \
            to"),
        choices=[
            (0, "0 replacements"),
            (1, "1 replacement"),
            (2, "2 replacements"),
            (3, "3 replacements"),
            (4, "4 replacements"),
            (5, "5 replacements"),
            (6, "6 replacements"),
            (7, "7 replacements"),
            (8, "8 replacements"),
            (9, "9 replacements"),
            (10, "10 replacements"),
        ]
    )
    c4_1_replacement_period = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("Replacement FDW period validity (months)"),
        choices=MONTH_CHOICES
    )
    c4_1_replacement_after_min_working_days = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("Replacement only after FDW has worked for minimum of \
            __ day(s)"),
        choices=DAY_CHOICES
    )
    c4_1_5_replacement_deadline = models.PositiveSmallIntegerField(
        # months
        verbose_name=_("Replacement FDW provided within __ month(s) from \
            date FDW returned"),
        choices=MONTH_CHOICES
    )
    c5_1_1_deployment_deadline = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("Deploy FDW to Employer within __ day(s) of date of \
            Service Agreement"),
        choices=DAY_CHOICES
    )
    c5_1_1_failed_deployment_refund = models.PositiveIntegerField(
        # cents
        verbose_name=_("Failed FDW deployment refund amount"),
    )
    c5_1_2_refund_within_days = models.PositiveIntegerField(
        # days
        verbose_name=_("If Employer terminates Agreement, Employer entitled \
            to Service Fee refund within __ day(s)"),
        choices=DAY_CHOICES
    )
    c5_1_2_before_fdw_arrives_charge = models.PositiveIntegerField(
        # cents
        verbose_name=_("Charge if Employer terminates BEFORE FDW arrives in \
            Singapore"),
    )
    c5_1_2_after_fdw_arrives_charge = models.PositiveIntegerField(
        # cents
        verbose_name=_("Charge if Employer terminates AFTER FDW arrives in \
            Singapore"),
    )
    c5_2_2_can_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=WEEK_CHOICES
    )
    c5_3_2_cannot_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        verbose_name=_("If new FDW deployed to Employer and former FDW CAN \
            be transferred to new employer, refund within __ week(s)"),
        choices=WEEK_CHOICES
    )
    c6_4_per_day_food_accommodation_cost = models.PositiveSmallIntegerField(
        # cents
        verbose_name=_("Accommodation cost per day"),
    )
    c6_6_per_session_counselling_cost = models.PositiveIntegerField(
        # cents
        verbose_name=_("Counselling cost per day"),
    )
    c9_1_independent_mediator_1 = models.CharField(
        verbose_name=_("Independent mediator #1"),
        max_length=40
    )
    c9_2_independent_mediator_2 = models.CharField(
        verbose_name=_("Independent mediator #2"),
        max_length=40
    )
    c13_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("Service Agreement termination notice (days)"),
        choices=DAY_CHOICES
    )

    # Employment Contract
    c3_5_fdw_sleeping_arrangement = models.CharField(
        verbose_name=_("FDW sleeping arrangement"),
        max_length=40,
        choices=[
            ("Have own room","Have own room"),
            ("Sharing room with someone","Sharing room with someone"),
            ("Sleeping in common area","Sleeping in common area"),
        ]
    )
    c4_1_termination_notice = models.PositiveSmallIntegerField(
        # days
        verbose_name=_("Employment Contract termination notice (days)"),
        choices=DAY_CHOICES
    )

class EmployerDocSig(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_signatures_ed'
    )
    agreement_date = models.DateField(
        verbose_name=_('Agreement Date for Signed Documents'),
        blank=True,
        null=True
    )
    employer_signature = models.TextField(
        verbose_name=_('Employer Signature'),
        blank=True,
        null=True
    )
    fdw_signature = models.TextField(
        verbose_name=_('FDW Signature'),
        blank=True,
        null=True
    )
    agency_staff_signature = models.TextField(
        verbose_name=_('Agency Staff Member Signature'),
        blank=True,
        null=True
    )
    spouse_signature = models.TextField(
        verbose_name=_('Spouse Signature'),
        blank=True,
        null=True
    )
    spouse_name = models.CharField(
        verbose_name=_('Spouse Name'),
        max_length=40,
        blank=True,
        null=True
    )
    spouse_nric = models.CharField(
        verbose_name=_('Spouse NRIC/FIN'),
        max_length=20,
        blank=True,
        null=True
    )
    sponsor_signature = models.TextField(
        verbose_name=_('Employer Sponsor Signature'),
        blank=True,
        null=True
    )

    # Verification Tokens
    employer_slug = models.SlugField(
        max_length=36,
        default=uuid.uuid4,
        unique=True
    )
    employer_token = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    fdw_slug = models.SlugField(
        max_length=36,
        default=uuid.uuid4,
        unique=True
    )
    fdw_token = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    # Witnesses
    employer_witness_signature = models.TextField(
        verbose_name=_('Signature of Witness for Employer'),
        blank=True,
        null=True
    )
    employer_witness_name = models.CharField(
        verbose_name=_('Employer Witness Name'),
        max_length=40,
        blank=True,
        null=True
    )
    employer_witness_nric = models.CharField(
        verbose_name=_('Last 4 characters of NRIC/FIN'),
        max_length=4,
        blank=True,
        null=True
    )
    fdw_witness_signature = models.TextField(
        verbose_name=_('Signature of Witness for FDW'),
        blank=True,
        null=True
    )
    fdw_witness_name = models.CharField(
        verbose_name=_('FDW Witness Name'),
        max_length=40,
        blank=True,
        null=True
    )
    fdw_witness_nric = models.CharField(
        verbose_name=_('Last 4 characters of NRIC/FIN'),
        max_length=4,
        blank=True,
        null=True
    )
    agency_staff_witness_signature = models.TextField(
        verbose_name=_('Signature of Witness for Agency Staff Memeber'),
        blank=True,
        null=True
    )
    agency_staff_witness_name = models.CharField(
        verbose_name=_('Agency Staff Memeber Witness Name'),
        max_length=40,
        blank=True,
        null=True
    )
    agency_staff_witness_nric = models.CharField(
        verbose_name=_('Last 4 characters of NRIC/FIN'),
        max_length=4,
        blank=True,
        null=True
    )

class EmployerDocMaidStatus(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_maidstatus_ed'
    )
    ipa_approval_date = models.DateField(
        verbose_name=_('In Principle Approval (IPA) Date'),
        blank=True,
        null=True
    )
    security_bond_approval_date = models.DateField(
        verbose_name=_('Security Bond Approval Date'),
        blank=True,
        null=True
    )
    arrival_date = models.DateField(
        verbose_name=_('FDW Arrival Date'),
        blank=True,
        null=True
    )
    thumb_print_date = models.DateField(
        verbose_name=_('FDW Thumb Print Date'),
        blank=True,
        null=True
    )
    sip_date = models.DateField(
        verbose_name=_('Settling-In Programme (SIP) Date'),
        blank=True,
        null=True
    )
    fdw_work_commencement_date = models.DateField(
        verbose_name=_('FDW Work Commencement Date'),
        blank=True,
        null=True
    )
    work_permit_no = models.CharField(
        verbose_name=_('Work Permit Number'),
        max_length=20,
        blank=True,
        null=True
    )

# from onlinemaid.storage_backends import PrivateMediaStorage
class JobOrder(models.Model):
    employer_doc = models.OneToOneField(
        EmployerDoc,
        on_delete=models.CASCADE,
        related_name='rn_joborder_ed'
    )
    slug = models.SlugField(
        max_length=100,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    job_order_pdf = models.FileField(
        verbose_name=_('Upload Job Order (PDF)'),
        upload_to=generate_joborder_path,
        blank=True,
        null=True,
        # storage=PrivateMediaStorage(),
        storage=OverwriteStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
