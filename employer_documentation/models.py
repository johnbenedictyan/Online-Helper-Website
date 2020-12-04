# Imports from python
# import uuid

# Imports from django
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

# Imports from other apps
from agency.models import AgencyEmployee
from maid.models import Maid

# Imports from within the app

# Utiliy Classes and Functions

# Start of Models

# Employer e-Documentation Models
'''
EmployerBase model holds minimum data required to create an Employer db entry
'''
class EmployerBase(models.Model):
    ######## To change to UUID for pk after initial testing ########
    # id = models.UUIDField(
    #     primary_key=True,
    #     default=uuid.uuid4,
    #     editable=False
    # )
    agency_employee = models.ForeignKey(
        AgencyEmployee,
        on_delete=models.RESTRICT
    )
    employer_name = models.CharField(max_length=40)
    employer_email = models.EmailField(
        verbose_name=_('Email Address'),
        blank=False
    )
    employer_mobile_number = models.CharField(
        verbose_name=_('Mobile Number'),
        max_length=10,
        blank=False,
        null=True,
        validators=[
            RegexValidator(
                regex='^[0-9]*$',
                message=_('Please enter a valid contact number')
            )
        ]
        # This regex validator checks if the contact number provided is all 
        # numbers.
    )

class EmployerExtraInfo(models.Model):
    employer_base = models.OneToOneField(
        EmployerBase,
        on_delete=models.CASCADE,
        related_name='rn_employerextrainfo'
    )
    employer_nric = models.CharField(max_length=20)
    employer_address_1 = models.CharField(
        verbose_name=_('Street Address'),
        max_length=100,
        blank=False,
        null=True
    )

    employer_address_2 = models.CharField(
        verbose_name=_('Unit Number'),
        max_length=50,
        blank=False,
        null=True
    )

    employer_postal_code = models.CharField(
        verbose_name=_('Postal Code'),
        max_length=25,
        blank=False,
        null=True
    )

'''
One to Many relationship with EmployerBase model so that agency is able to
sign subsequent agreements with same employer
'''
class EmployerDocBase(models.Model):
    case_ref_no = models.CharField(
        max_length=20,
        unique=True
    )
    employer = models.ForeignKey(
        EmployerBase,
        on_delete=models.RESTRICT,
        related_name='rn_employerdocbase'
    )
    fdw = models.ForeignKey(
        Maid,
        on_delete=models.RESTRICT
    )
    spouse_required = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    sponsor_required = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )

class EmployerDocSig(models.Model):
    employer_doc_base = models.OneToOneField(
        EmployerDocBase,
        on_delete=models.CASCADE
    )
    agreement_date = models.DateField(blank=True, null=True)
    # employer_signature = ImageField(blank=True, null=True)
    # spouse_signature = ImageField(blank=True,null=True)
    # sponsor_signature = ImageField(blank=True, null=True)
    # fdw_signature = ImageField(blank=True, null=True)
    # sales_staff_signature = ImageField(blank=True, null=True)

    # employer_signature_native = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    # spouse_signature_native = models.ImageField(blank=True,null=True, upload_to=get_file_path)
    # sponsor_signature_native = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    # fdw_signature_native = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    # sales_staff_signature_native = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    # One-time token sent to employer for them to get their signature
    # employer_signature_token = models.CharField(max_length=32, blank=True, null=True)

class EmployerDocJobOrder(models.Model):
    employer_doc_base = models.OneToOneField(
        EmployerDocBase,
        on_delete=models.CASCADE,
        related_name='rn_employerdocjoborder'
    )
    job_order_date = models.DateField()
    employer_race = models.CharField(
        max_length=16,
        choices = [
            ("Chinese", "Chinese"),
            ("Malay", "Malay"),
            ("Indian", "Indian"),
            ("Others", "Others")
        ]
    )
    type_of_property_choices = [
        ("HDB 2 Room flat", "HDB 2 Room flat"),
        ("HDB 3 Room flat", "HDB 3 Room flat"),
        ("HDB 4 Room flat", "HDB 4 Room flat"),
        ("HDB 5 Room flat", "HDB 5 Room flat"),
        ("HDB Executive flat","HDB Executive flat"),
        ("HDB Maisonette flat","HDB Maisonette flat"),
        ("Condominium","Condominium"),
        ("Penthouse","Penthouse"),
        ("Terrace","Terrace"),
        ("Semi-Detached","Semi-Detached"),
        ("Bungalow","Bungalow"),
        ("Shophouse","Shophouse"),
    ]
    type_of_property = models.CharField(
        max_length=40,
        choices = type_of_property_choices
    )
    no_of_bedrooms = models.PositiveSmallIntegerField(
        choices=[
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10")
        ]
    )
    no_of_toilets = models.PositiveSmallIntegerField(
        choices=[
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
    no_of_family_members = models.PositiveSmallIntegerField(
        choices=[
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
        ]
    )
    no_of_children_between_6_12 = models.PositiveSmallIntegerField(
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
    no_of_children_below_5 = models.PositiveSmallIntegerField(
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
    no_of_infants = models.PositiveSmallIntegerField(
        choices=[
            (0, "0"),
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
        ]
    )
    fetch_children = models.TextField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    look_after_elderly = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    look_after_bed_ridden_patient = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    cooking = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    clothes_washing = models.CharField(max_length=10,
        choices = [
            ("Hand","Hand"),
            ("Machine","Machine"),
            ("Both","Both")
        ]
    )
    car_washing = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    take_care_of_pets = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    gardening = models.CharField(max_length=3,
        choices = [
            ("Yes","Yes"),
            ("No","No")
        ]
    )
    remarks = models.TextField(max_length=300, blank=True, null=True)

    def job_order_date(self):
        return self.job_order_date.strftime('%d/%m/%Y')

class EmployerDocMaidStatus(models.Model):
    employer_doc_base = models.OneToOneField(
        EmployerDocBase,
        on_delete=models.CASCADE
    )
    ipa_approval_date = models.DateField(blank=True, null=True)
    security_bond_approval_date = models.DateField(blank=True, null=True)
    arrival_date = models.DateField(blank=True, null=True)
    thumb_print_date = models.DateField(blank=True, null=True)
    sip_date = models.DateField(blank=True, null=True)
    fdw_work_commencement_date = models.DateField(blank=True, null=True)
    date_of_application_for_transfer = models.DateField(blank=True, null=True)

    def date_of_application_for_transfer(self):
        return self.date_of_application_for_transfer.strftime('%d/%m/%Y')
    
    def fdw_work_commencement_date(self):
        return self.fdw_work_commencement_date.strftime('%d/%m/%Y')

class EmployerDocServiceFeeBase(models.Model):
    employer_doc_base = models.OneToOneField(
        EmployerDocBase,
        on_delete=models.CASCADE,
        related_name='rn_employerdocservicefeebase'
    )
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

class EmployerDocServiceFeeReplacement(models.Model):
    service_fee_schedule = models.OneToOneField(
        EmployerDocServiceFeeBase,
        on_delete=models.CASCADE
    )
    fdw_replaced = models.ForeignKey(
        Maid,
        on_delete=models.RESTRICT
    )
    b4_loan_transferred = models.PositiveIntegerField()

class EmployerDocServiceAgreement(models.Model):
    employer_doc_base = models.OneToOneField(
        EmployerDocBase,
        on_delete=models.CASCADE
    )
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

class EmployerDocEmploymentContract(models.Model):
    employer_doc_base = models.OneToOneField(
        EmployerDocBase,
        on_delete=models.CASCADE
    )
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

# class EmployerDocSalaryPlacementRepayment(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocRestDayAgreement(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocHandoverChecklist(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocTransferConsent(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocWorkPassAuthorisation(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocSecurityBondForm(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocWorkPermitApplicants(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocIncomeTaxDeclaration(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )

# class EmployerDocSafetyAgreement(models.Model):
#     employer_doc_base = models.OneToOneField(
#         EmployerDocBase,
#         on_delete=models.CASCADE
#     )
