# Imports from django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column
from crispy_forms.bootstrap import FormActions

# Imports from local apps
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
)
# from .mixins import SignatureFormMixin
from agency.models import AgencyEmployee
# from maid.models import Maid
from . import mixins as ed_mixins


# Start of Forms
class EmployerForm(forms.ModelForm):
    class Meta:
        model = Employer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.user_obj = get_user_model().objects.get(pk=self.user_pk)
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-base-form'

        ef_fieldset_all = Fieldset(
            # Legend for form
            'Create new / update existing employer:',
            # Form fields
            'agency_employee',
            'employer_name',
            'employer_email',
            'employer_mobile_number',
            'employer_nric',
            'employer_address_1',
            'employer_address_2',
            'employer_post_code',
        )
        ef_fieldset_exclude_agencyemployee = Fieldset(
            # Legend for form
            'Create new / update existing employer:',
            # Form fields
            'employer_name',
            'employer_email',
            'employer_mobile_number',
            'employer_nric',
            'employer_address_1',
            'employer_address_2',
            'employer_post_code',
        )

        if self.agency_user_group==ed_mixins.AG_OWNERS:
            print(self.agency_user_group)
            self.helper.layout = Layout(
                ef_fieldset_all,
                Submit('submit', 'Submit')
            )
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_owner.agency
                )
            )
        elif self.agency_user_group==ed_mixins.AG_ADMINS:
            self.helper.layout = Layout(
                ef_fieldset_all,
                Submit('submit', 'Submit')
            )
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_employee.agency
                )
            )
        elif self.agency_user_group==ed_mixins.AG_MANAGERS:
            self.helper.layout = Layout(
                ef_fieldset_all,
                Submit('submit', 'Submit')
            )
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    branch=self.user_obj.agency_employee.branch
                )
            )
        else:
            del self.fields['agency_employee']
            self.helper.layout = Layout(
                ef_fieldset_exclude_agencyemployee,
                Submit('submit', 'Submit')
            )
    
    def check_queryset(self, queryset, error_msg):
        for employer_obj in queryset:
            if not employer_obj==self.instance:
                # Check if it belongs to current user's agency
                if self.agency_user_group==ed_mixins.AG_OWNERS:
                    if (
                        employer_obj.agency_employee.agency
                        == self.user_obj.agency_owner.agency
                    ):
                        raise ValidationError(error_msg)
                elif (
                    employer_obj.agency_employee.agency
                    == self.user_obj.agency_employee.agency
                ):
                    raise ValidationError(error_msg)
    
    def clean_employer_email(self):
        cleaned_field = self.cleaned_data['employer_email']

        try:
            # Check if employer_email exists in database
            employer_queryset = Employer.objects.filter(
                employer_email=cleaned_field
            )
        except Employer.DoesNotExist:
            # If no entries for employer_email, then no further checks
            return cleaned_field
        else:
            self.check_queryset(
                employer_queryset,
                'An employer with this email address already exists in your \
                    agency'
            )
        return cleaned_field

    def clean_employer_mobile_number(self):
        cleaned_field = self.cleaned_data['employer_mobile_number']

        try:
            # Check if employer_mobile_number exists in database
            employer_queryset = Employer.objects.filter(
                employer_mobile_number=cleaned_field
            )
        except Employer.DoesNotExist:
            # If no entries for employer_mobile_number, then no further checks
            return cleaned_field
        else:
            self.check_queryset(
                employer_queryset,
                'An employer with this mobile number already exists in your \
                    agency'
            )
        return cleaned_field

    def clean_employer_nric(self):
        cleaned_field = self.cleaned_data['employer_nric']

        try:
            # Check if employer_nric exists in database
            employer_queryset = Employer.objects.filter(
                employer_nric=cleaned_field
            )
        except Employer.DoesNotExist:
            # If no entries for employer_nric, then no further checks
            return cleaned_field
        else:
            self.check_queryset(
                employer_queryset,
                'An employer with this NRIC/FIN already exists in your \
                    agency'
            )
        return cleaned_field

# class EmployerAgentForm(forms.ModelForm):
#     class Meta:
#         model = Employer
#         fields = ['agency_employee']

#     def __init__(self, *args, **kwargs):
#         self.user_pk = kwargs.pop('user_pk')
#         super().__init__(*args, **kwargs)
#         user_obj = AgencyEmployee.objects.get(pk=self.user_pk)

#         if (
#             # If current user is part of owner or administrator group,
#             # display all agency's employees
#             user_obj.user.groups.filter(name=ed_mixins.AG_OWNERS)
#             .exists()
#             or
#             user_obj.user.groups.filter(name=ed_mixins.AG_ADMINS)
#             .exists()
#         ):
#             self.fields['agency_employee'].queryset = (
#                 AgencyEmployee.objects.filter(agency=user_obj.agency)
#             )
#         elif (
#             # If current user is part of manager group, display all agency
#             # branches employees
#             user_obj.user.groups.filter(name=ed_mixins.AG_MANAGERS)
#             .exists()
#         ):
#             self.fields['agency_employee'].queryset = (
#                 AgencyEmployee.objects.filter(branch=user_obj.branch)
#             )
#         else:
#             # If current user is not part of owner, administrator or manager
#             # group, only provide unusable choice that will fail validation.
#             # View should also perform separate user permissions check.
#             self.fields['agency_employee'].choices = [('-','-')]
        
#         self.helper = FormHelper()
#         self.helper.form_class = 'employer-base-form'
#         self.helper.layout = Layout(
#             Fieldset(
#                 # Legend for form
#                 "Update employer's assigned agency employee:",
#                 # Form fields
#                 'agency_employee',
#             ),
#             Submit('submit', 'Submit')
#         )

# class EmployerDocBaseForm(forms.ModelForm):
#     class Meta:
#         model = EmployerDocBase
#         exclude = ['employer']

#     def __init__(self, *args, **kwargs):
#         self.user_pk = kwargs.pop('user_pk')
#         self.agency_user_group = kwargs.pop('agency_user_group')
#         super().__init__(*args, **kwargs)

#         if self.agency_user_group==ed_mixins.AG_OWNERSs:
#             self.fields['fdw'].queryset = (
#                 Maid.objects.filter(agency=get_user_model().objects.get(
#                     pk=self.user_pk).agency_owner.agency)
#             )
#         else:
#             self.fields['fdw'].queryset = (
#                 Maid.objects.filter(agency=get_user_model().objects.get(
#                     pk=self.user_pk).agency_employee.agency)
#             )
        
#         self.helper = FormHelper()
#         self.helper.form_class = 'employer-doc-form'
#         self.helper.layout = Layout(
#             Fieldset(
#                 # Legend for form
#                 'Create new / update existing employer doc base:',
#                 # Form fields
#                 'case_ref_no',
#                 'fdw',
#                 'spouse_required',
#                 'sponsor_required',
#             ),
#             Submit('submit', 'Submit')
#         )

# class EmployerDocServiceFeeBaseForm(forms.ModelForm):
#     class Meta:
#         model = EmployerDocServiceFeeBase
#         exclude = ['employer_doc_base']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_class = 'employer-doc-form'
#         self.helper.layout = Layout(
#             Fieldset(
#                 # Legend for form
#                 'Create new / update existing employer doc service fee base:',
#                 # Form fields
#                 'b1_service_fee',
#                 'b2a_work_permit_application_collection',
#                 'b2b_medical_examination_fee',
#                 'b2c_security_bond_accident_insurance',
#                 'b2d_indemnity_policy_reimbursement',
#                 'b2e_home_service',
#                 'b2f_counselling',
#                 'b2g_sip',
#                 'b2h_replacement_months',
#                 'b2h_replacement_cost',
#                 'b2i_work_permit_renewal',
#                 'b2j1_other_services_description',
#                 'b2j1_other_services_fee',
#                 'b2j2_other_services_description',
#                 'b2j2_other_services_fee',
#                 'b2j3_other_services_description',
#                 'b2j3_other_services_fee',
#                 'ca_deposit',
#             ),
#             Submit('submit', 'Submit')
#         )

# class EmployerDocServiceAgreementForm(forms.ModelForm):
#     class Meta:
#         model = EmployerDocServiceAgreement
#         exclude = ['employer_doc_base']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_class = 'employer-doc-form'
#         self.helper.layout = Layout(
#             Fieldset(
#                 # Legend for form
#                 'Create new / update existing employer doc service agreement:',
#                 # Form fields
#                 'c1_3_handover_days',
#                 'c3_2_no_replacement_criteria_1',
#                 'c3_2_no_replacement_criteria_2',
#                 'c3_2_no_replacement_criteria_3',
#                 'c3_4_no_replacement_refund',
#                 'c4_1_number_of_replacements',
#                 'c4_1_replacement_period',
#                 'c4_1_replacement_after_min_working_days',
#                 'c4_1_5_replacement_deadline',
#                 'c5_1_1_deployment_deadline',
#                 'c5_1_1_failed_deployment_refund',
#                 'c5_1_2_refund_within_days',
#                 'c5_1_2_before_fdw_arrives_charge',
#                 'c5_1_2_after_fdw_arrives_charge',
#                 'c5_2_2_can_transfer_refund_within',
#                 'c5_3_2_cannot_transfer_refund_within',
#                 'c6_4_per_day_food_accommodation_cost',
#                 'c6_6_per_session_counselling_cost',
#                 'c9_1_independent_mediator_1',
#                 'c9_2_independent_mediator_2',
#                 'c13_termination_notice',
#             ),
#             Submit('submit', 'Submit')
#         )

# class EmployerDocEmploymentContractForm(forms.ModelForm):
#     class Meta:
#         model = EmployerDocEmploymentContract
#         exclude = ['employer_doc_base']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_class = 'employer-doc-form'
#         self.helper.layout = Layout(
#             Fieldset(
#                 # Legend for form
#                 'Create new / update existing employer doc employment contract:',
#                 # Form fields
#                 'c3_2_salary_payment_date',
#                 'c3_5_fdw_sleeping_arrangement',
#                 'c4_1_termination_notice',
#             ),
#             Submit('submit', 'Submit')
#         )


# # Signature Forms
# class SignatureEmployerForm(SignatureFormMixin, forms.ModelForm):
#     class Meta:
#         model = EmployerDocSig
#         fields = ['employer_signature']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.model_field_name = 'employer_signature'
#         self.fields[self.model_field_name].widget.attrs.update(
#             {
#                 'id': 'id_signature',
#                 'hidden': 'true',
#             }
#         )

# class SignatureSpouseForm(SignatureFormMixin, forms.ModelForm):
#     class Meta:
#         model = EmployerDocSig
#         fields = ['spouse_signature']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.model_field_name = 'spouse_signature'
#         self.fields[self.model_field_name].widget.attrs.update(
#             {
#                 'id': 'id_signature',
#                 'hidden': 'true',
#             }
#         )

# class SignatureSponsorForm(SignatureFormMixin, forms.ModelForm):
#     class Meta:
#         model = EmployerDocSig
#         fields = ['sponsor_signature']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.model_field_name = 'sponsor_signature'
#         self.fields[self.model_field_name].widget.attrs.update(
#             {
#                 'id': 'id_signature',
#                 'hidden': 'true',
#             }
#         )

# class SignatureFdwForm(SignatureFormMixin, forms.ModelForm):
#     class Meta:
#         model = EmployerDocSig
#         fields = ['fdw_signature']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.model_field_name = 'fdw_signature'
#         self.fields[self.model_field_name].widget.attrs.update(
#             {
#                 'id': 'id_signature',
#                 'hidden': 'true',
#             }
#         )

# class SignatureAgencyStaffForm(SignatureFormMixin, forms.ModelForm):
#     class Meta:
#         model = EmployerDocSig
#         fields = ['agency_staff_signature']
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.model_field_name = 'agency_staff_signature'
#         self.fields[self.model_field_name].widget.attrs.update(
#             {
#                 'id': 'id_signature',
#                 'hidden': 'true',
#             }
#         )
