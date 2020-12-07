# Imports from django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column
from crispy_forms.bootstrap import FormActions

# Imports from local apps
from .models import (
    EmployerBase,
    EmployerDocBase,
    EmployerDocEmploymentContract,
    EmployerDocJobOrder,
    EmployerDocMaidStatus,
    EmployerDocServiceAgreement,
    EmployerDocServiceFeeBase,
    EmployerDocServiceFeeReplacement,
    EmployerDocSig,
    EmployerExtraInfo,
)


# Start of Forms

# Forms that inherit from inbuilt Django forms

# Model Forms (forms.ModelForm)
class EmployerBaseForm(forms.ModelForm):
    class Meta:
        model = EmployerBase
        exclude = ['agency_employee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-base-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer:',
                # Form fields
                'employer_name',
                'employer_email',
                'employer_mobile_number',
            ),
            Submit('submit', 'Submit')
        )

class EmployerExtraInfoForm(forms.ModelForm):
    class Meta:
        model = EmployerExtraInfo
        exclude = ['employer_base','agency_employee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-base-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer extra info:',
                # Form fields
                'employer_nric',
                'employer_address_1',
                'employer_address_2',
                'employer_postal_code',
            ),
            Submit('submit', 'Submit')
        )

class EmployerDocBaseForm(forms.ModelForm):
    class Meta:
        model = EmployerDocBase
        exclude = ['employer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer doc base:',
                # Form fields
                'case_ref_no',
                'fdw',
                'spouse_required',
                'sponsor_required',
            ),
            Submit('submit', 'Submit')
        )

class EmployerDocJobOrderForm(forms.ModelForm):
    class Meta:
        model = EmployerDocJobOrder
        exclude = ['employer_doc_base']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer doc job order:',
                # Form fields
                'job_order_date', ################################################# bug - does not show in form
                'employer_race',
                'type_of_property',
                'no_of_bedrooms',
                'no_of_toilets',
                'no_of_family_members',
                'no_of_children_between_6_12',
                'no_of_children_below_5',
                'no_of_infants',
                'fetch_children',
                'look_after_elderly',
                'look_after_bed_ridden_patient',
                'cooking',
                'clothes_washing',
                'car_washing',
                'take_care_of_pets',
                'gardening',
                'remarks',
            ),
            Submit('submit', 'Submit')
        )

class EmployerDocServiceFeeBaseForm(forms.ModelForm):
    class Meta:
        model = EmployerDocServiceFeeBase
        exclude = ['employer_doc_base']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer doc service fee base:',
                # Form fields
                'b1_service_fee',
                'b2a_work_permit_application_collection',
                'b2b_medical_examination_fee',
                'b2c_security_bond_accident_insurance',
                'b2d_indemnity_policy_reimbursement',
                'b2e_home_service',
                'b2f_counselling',
                'b2g_sip',
                'b2h_replacement_months',
                'b2h_replacement_cost',
                'b2i_work_permit_renewal',
                'b2j1_other_services_description',
                'b2j1_other_services_fee',
                'b2j2_other_services_description',
                'b2j2_other_services_fee',
                'b2j3_other_services_description',
                'b2j3_other_services_fee',
                'ca_deposit',
            ),
            Submit('submit', 'Submit')
        )

class EmployerDocServiceAgreementForm(forms.ModelForm):
    class Meta:
        model = EmployerDocServiceAgreement
        exclude = ['employer_doc_base']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer doc service agreement:',
                # Form fields
                'c1_3_handover_days',
                'c3_2_no_replacement_criteria_1',
                'c3_2_no_replacement_criteria_2',
                'c3_2_no_replacement_criteria_3',
                'c3_4_no_replacement_refund',
                'c4_1_number_of_replacements',
                'c4_1_replacement_period',
                'c4_1_5_replacement_deadline',
                'c5_1_1_deployment_deadline',
                'c5_1_1_failed_deployment_refund',
                'c5_1_2_before_fdw_arrives_charge',
                'c5_1_2_after_fdw_arrives_charge',
                'c5_2_2_can_transfer_refund_within',
                'c5_3_2_cannot_transfer_refund_within',
                'c6_4_per_day_food_accommodation_cost',
                'c6_6_per_session_counselling_cost',
                'c9_1_independent_mediator_1',
                'c9_2_independent_mediator_2',
                'c13_termination_notice',
            ),
            Submit('submit', 'Submit')
        )

class EmployerDocEmploymentContractForm(forms.ModelForm):
    class Meta:
        model = EmployerDocEmploymentContract
        exclude = ['employer_doc_base']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer doc employment contract:',
                # Form fields
                'c3_2_salary_payment_date',
                'c3_5_fdw_sleeping_arrangement',
                'c4_1_termination_notice',
            ),
            Submit('submit', 'Submit')
        )


# Generic Forms (forms.Form)
