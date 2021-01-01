# Imports from python
import uuid

# Imports from django
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

# Imports from other apps
from onlinemaid.constants import TrueFalseChoices
from agency.models import AgencyEmployee
from maid.models import Maid

# Imports from within the app

# Utiliy Classes and Functions

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
                regex='^[8-9][0-9]{7}$',
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
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    case_ref_no = models.CharField(
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
        on_delete=models.RESTRICT
    )
    spouse_required = models.BooleanField(
        verbose_name=_("Is spouse requried? A spouse required if Employer's \
            monthly income < S$3,000 per month."),
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
    b1_service_fee = models.PositiveIntegerField() # cents
    b2a_work_permit_application_collection = models.PositiveIntegerField() # cents
    b2b_medical_examination_fee = models.PositiveIntegerField() # cents
    b2c_security_bond_accident_insurance = models.PositiveIntegerField() # cents
    b2d_indemnity_policy_reimbursement = models.PositiveIntegerField() # cents
    b2e_home_service = models.PositiveIntegerField() # cents
    b2f_counselling = models.PositiveIntegerField() # cents
    b2g_sip = models.PositiveIntegerField() # cents
    b2h_replacement_months = models.PositiveSmallIntegerField(
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
        ]
    )
    b2h_replacement_cost = models.PositiveIntegerField() # cents
    b2i_work_permit_renewal = models.PositiveIntegerField() # cents
    b2j1_other_services_description = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )
    b2j1_other_services_fee = models.PositiveIntegerField(
        blank=True,
        null=True
    ) # cents
    b2j2_other_services_description = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )
    b2j2_other_services_fee = models.PositiveIntegerField(
        blank=True,
        null=True
    ) # cents
    b2j3_other_services_description = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )
    b2j3_other_services_fee = models.PositiveIntegerField(
        blank=True,
        null=True
    ) # cents
    ca_deposit = models.PositiveIntegerField() # cents

    # If FDW is replacement, then additional fields
    fdw_is_replacement = models.BooleanField()
    fdw_replaced = models.ForeignKey(
        Maid,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name='rn_ed_fdwreplaced'
    )
    b4_loan_transferred = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    # Service Agreement
    c1_3_handover_days = models.PositiveSmallIntegerField(
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
            (25, "25"),
            (26, "26"),
            (27, "27"),
            (28, "28"),
            (29, "29"),
            (30, "30"),
        ]
    )
    c3_2_no_replacement_criteria_1 = models.CharField(max_length=100)
    c3_2_no_replacement_criteria_2 = models.CharField(max_length=100)
    c3_2_no_replacement_criteria_3 = models.CharField(max_length=100)
    c3_4_no_replacement_refund = models.PositiveIntegerField()
    c4_1_number_of_replacements = models.PositiveSmallIntegerField(
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
        ]
    )
    c4_1_replacement_period = models.PositiveSmallIntegerField(
        # months
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
        ]
    )
    c4_1_replacement_after_min_working_days = models.PositiveSmallIntegerField(
        # days
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
            (25, "25"),
            (26, "26"),
            (27, "27"),
            (28, "28"),
            (29, "29"),
            (30, "30"),
        ]
    )
    c4_1_5_replacement_deadline = models.PositiveSmallIntegerField(
        # months
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
        ]
    )
    c5_1_1_deployment_deadline = models.PositiveSmallIntegerField(
        # days
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
            (25, "25"),
            (26, "26"),
            (27, "27"),
            (28, "28"),
            (29, "29"),
            (30, "30"),
        ]
    )
    c5_1_1_failed_deployment_refund = models.PositiveIntegerField()
    c5_1_2_refund_within_days = models.PositiveIntegerField(
        # days
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
            (25, "25"),
            (26, "26"),
            (27, "27"),
            (28, "28"),
            (29, "29"),
            (30, "30"),
        ]
    )
    c5_1_2_before_fdw_arrives_charge = models.PositiveIntegerField()
    c5_1_2_after_fdw_arrives_charge = models.PositiveIntegerField()
    c5_2_2_can_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
        ]
    )
    c5_3_2_cannot_transfer_refund_within = models.PositiveSmallIntegerField(
        # weeks
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
        ]
    )
    c6_4_per_day_food_accommodation_cost = models.PositiveSmallIntegerField()
    c6_6_per_session_counselling_cost = models.PositiveIntegerField()
    c9_1_independent_mediator_1 = models.CharField(max_length=40)
    c9_2_independent_mediator_2 = models.CharField(max_length=40)
    c13_termination_notice = models.PositiveSmallIntegerField(
        # days
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
            (25, "25"),
            (26, "26"),
            (27, "27"),
            (28, "28"),
            (29, "29"),
            (30, "30"),
        ]
    )

    # Employment Contract
    c3_2_salary_payment_date = models.PositiveSmallIntegerField(
        # day of month
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
            (25, "25"),
            (26, "26"),
            (27, "27"),
            (28, "28"),
        ]
    )
    c3_5_fdw_sleeping_arrangement = models.CharField(
        max_length=40,
        choices=[
            ("Have own room","Have own room"),
            ("Sharing room with someone","Sharing room with someone"),
            ("Sleeping in common area","Sleeping in common area"),
        ]
    )
    c4_1_termination_notice = models.PositiveSmallIntegerField(
        # days
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (16, "16"),
            (17, "17"),
            (18, "18"),
            (19, "19"),
            (20, "20"),
            (21, "21"),
            (22, "22"),
            (23, "23"),
            (24, "24"),
            (25, "25"),
            (26, "26"),
            (27, "27"),
            (28, "28"),
            (29, "29"),
            (30, "30"),
        ]
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
        verbose_name='Spouse NRIC/FIN',
        max_length=20,
        blank=True,
        null=True
    )
    sponsor_signature = models.TextField(
        verbose_name=_('Employer Sponsor Signature'),
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
        verbose_name='Last 4 characters of NRIC/FIN',
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
        verbose_name='Last 4 characters of NRIC/FIN',
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
        verbose_name='Last 4 characters of NRIC/FIN',
        max_length=4,
        blank=True,
        null=True
    )

    # One-time token sent to employer for them to get their signature
    # employer_signature_token = models.CharField(max_length=32, blank=True, null=True)

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
    job_order_pdf = models.FileField(
        upload_to='employer-documentation/job-orders/',
        # storage=PrivateMediaStorage()
    )
