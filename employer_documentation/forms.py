# Python
import secrets

# Imports from django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML, Hidden
from crispy_forms.bootstrap import FormActions, PrependedAppendedText

# Imports from local apps
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
from agency.models import AgencyEmployee
from maid.models import Maid


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
        self.helper.form_class = 'employer-form'

        ef_fieldset_all = Fieldset(
            # Legend for form
            'Employer Details',
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
            'Employer Details',
            # Form fields
            'employer_name',
            'employer_email',
            'employer_mobile_number',
            'employer_nric',
            'employer_address_1',
            'employer_address_2',
            'employer_post_code',
        )

        if self.agency_user_group==AG_OWNERS:
            self.helper.layout = Layout(
                ef_fieldset_all,
                Submit('submit', 'Submit')
            )
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_owner.agency
                )
            )
        elif self.agency_user_group==AG_ADMINS:
            self.helper.layout = Layout(
                ef_fieldset_all,
                Submit('submit', 'Submit')
            )
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_employee.agency
                )
            )
        elif self.agency_user_group==AG_MANAGERS:
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
                if self.agency_user_group==AG_OWNERS:
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
        cleaned_field = self.cleaned_data.get('employer_email')

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
        cleaned_field = self.cleaned_data.get('employer_mobile_number')

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
        cleaned_field = self.cleaned_data.get('employer_nric')

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

class EmployerDocForm(forms.ModelForm):
    class Meta:
        model = EmployerDoc
        exclude = ['employer']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        if self.agency_user_group==AG_OWNERS:
            self.fields['fdw'].queryset = (
                Maid.objects.filter(agency=get_user_model().objects.get(
                    pk=self.user_pk).agency_owner.agency)
            )
            self.fields['fdw_replaced'].queryset = (
                Maid.objects.filter(agency=get_user_model().objects.get(
                    pk=self.user_pk).agency_owner.agency)
            )
        else:
            self.fields['fdw'].queryset = (
                Maid.objects.filter(agency=get_user_model().objects.get(
                    pk=self.user_pk).agency_employee.agency)
            )
            self.fields['fdw_replaced'].queryset = (
                Maid.objects.filter(agency=get_user_model().objects.get(
                    pk=self.user_pk).agency_employee.agency)
            )
        
        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            HTML(
                """
                <h3 class="mb-3">Documentation Details</h3>
                <h5 class="doc-section-header" id="id-doc-general">General</h5>
            """),
            Row(
                Column(
                    'case_ref_no',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'fdw',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'spouse_required',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'sponsor_required',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            # Service Fee Schedule - Form A
            HTML(
                """
                <h5 class="doc-section-header" id="id-doc-service-fee-schedule">Service Fee Schedule</h5>
            """),
            Row(
                Column(
                    PrependedAppendedText(
                        'b1_service_fee', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2a_work_permit_application_collection', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'b2b_medical_examination_fee', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2c_security_bond_accident_insurance', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'b2d_indemnity_policy_reimbursement', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2e_home_service', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'b2f_counselling', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2g_sip', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2h_replacement_months',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2h_replacement_cost', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'b2i_work_permit_renewal', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                # Column(
                #     PrependedAppendedText(
                #         '', '$', '.00'
                #     ),
                #     css_class='form-group col-md-6'
                # ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2j1_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2j1_other_services_fee', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2j2_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2j2_other_services_fee', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2j3_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b2j3_other_services_fee', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'ca_deposit', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'fdw_is_replacement',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            # Replacement - Service Fee Schedule - Form B
            Row(
                Column(
                    'fdw_replaced',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'b4_loan_transferred', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            # Service Agreement
            HTML(
                """
                <h5 class="doc-section-header" id="id-doc-service-agreement">Service Agreement</h5>
            """),
            Row(
                Column(
                    'c1_3_handover_days',
                    css_class='form-group col-md-6'
                ),
                # Column(
                #     PrependedAppendedText(
                #         '', '$', '.00'
                #     ),
                #     css_class='form-group col-md-6'
                # ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c3_2_no_replacement_criteria_1',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c3_2_no_replacement_criteria_2',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c3_2_no_replacement_criteria_3',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'c3_4_no_replacement_refund', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c4_1_number_of_replacements',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c4_1_replacement_period',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c4_1_replacement_after_min_working_days',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c4_1_5_replacement_deadline',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c5_1_1_deployment_deadline',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'c5_1_1_failed_deployment_refund', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c5_1_2_refund_within_days',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'c5_1_2_before_fdw_arrives_charge', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'c5_1_2_after_fdw_arrives_charge', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c5_2_2_can_transfer_refund_within',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c5_3_2_cannot_transfer_refund_within',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedAppendedText(
                        'c6_4_per_day_food_accommodation_cost', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedAppendedText(
                        'c6_6_per_session_counselling_cost', '$', '.00'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c9_1_independent_mediator_1',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c9_2_independent_mediator_2',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c13_termination_notice',
                    css_class='form-group col-md-6'
                ),
                # Column(
                #     '',
                #     css_class='form-group col-md-6'
                # ),
                css_class='form-row'
            ),
            # Employment Contract
            HTML(
                """
                <h5 class="doc-section-header" id="id-doc-employment-contract">Employment Contract</h5>
            """),
            Row(
                Column(
                    'c3_5_fdw_sleeping_arrangement',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c4_1_termination_notice',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            # Submit
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

    def clean_fdw_replaced(self):
        is_replacement = self.cleaned_data.get('fdw_is_replacement')
        cleaned_field = self.cleaned_data.get('fdw_replaced')

        if not is_replacement:
            return cleaned_field
        elif is_replacement and not cleaned_field:
            raise ValidationError('FDW being replaced is a required field')
        elif cleaned_field==self.cleaned_data.get('fdw'):
            raise ValidationError('Replacement FDW cannot be the same as new \
                FDW')
        else:
            return cleaned_field

    def clean_b4_loan_transferred(self):
        is_replacement = self.cleaned_data.get('fdw_is_replacement')
        cleaned_field = self.cleaned_data.get('b4_loan_transferred')

        if not is_replacement:
            return cleaned_field
        elif is_replacement and not cleaned_field:
            raise ValidationError('Loan being transferred is a required \
                field')
        else:
            return cleaned_field

class EmployerDocAgreementDateForm(forms.ModelForm):
    class Meta:
        model = EmployerDocSig
        fields = ['agreement_date']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Signing Date of Agreement',
                
                # Form fields - main
                'agreement_date',
            ),
            Submit('submit', 'Submit')
        )

class EmployerDocMaidStatusForm(forms.ModelForm):
    class Meta:
        model = EmployerDocMaidStatus
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Documentation Status Details',
                
                # Form fields - main
                'ipa_approval_date',
                'security_bond_approval_date',
                'arrival_date',
                'thumb_print_date',
                'sip_date',
                'fdw_work_commencement_date',
                'work_permit_no',
            ),
            Submit('submit', 'Submit')
        )

class JobOrderForm(forms.ModelForm):
    class Meta:
        model = JobOrder
        widgets = {'job_order_pdf': forms.FileInput(attrs={'accept': 'application/pdf'})}
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                '',
                
                # Form fields - main
                'job_order_pdf',
            ),
            Submit('submit', 'Submit')
        )


# Signature Forms
class SignatureForm(forms.ModelForm):
    class Meta:
        model = EmployerDocSig
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        # Assign model_field_name in urls.py or views.py
        self.model_field_name = kwargs.pop('model_field_name')
        self.form_fields = kwargs.pop('form_fields')
        super().__init__(*args, **kwargs)

        # Make copy of all field names, then remove fields that are not
        # in self.form_fields.
        fields_copy = list(self.fields)
        for field in fields_copy:
            if field not in self.form_fields:
                del self.fields[field]
        
        # Instantiate blank Layout instance
        self.helper = FormHelper()
        self.helper.form_class = 'employer-docsig-form'
        self.helper.layout = Layout()

        # Append form fields to Layout instance
        for field in self.fields:
            if field==self.model_field_name:
                self.helper.layout.append(
                    Hidden(self.model_field_name, self.model_field_name, id='id_signature'),
                )
            else:
                self.helper.layout.append(
                    Row(
                        Column(field, css_class='form-group col'),
                        css_class='form-row'
                    ),
                )

        # Signature pad
        self.helper.layout.append(
            Row(
                Column(
                    HTML("""
                        <canvas
                            id="signature-pad"
                            class=""
                            style="border: 1px solid #d2d2d2"
                        >
                        </canvas>
                    """)
                ),
                css_class='form-row'
            )
        )
        # Label for signature pad
        self.helper.layout.append(
            Row(
                Column(
                    HTML("""
                        <h6>{{ model_field_verbose_name }}</h6>
                    """)
                ),
                css_class='form-row'
            )
        )
        # Submit form and clear signature pad buttons
        self.helper.layout.append(
            Row(
                Column(
                    Submit("submit", "Submit"),
                    HTML("""
                        <a href="#" onclick="signaturePad.clear()" class="btn btn-secondary">Clear</a>
                    """)
                ),
                css_class='form-row'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        base64_sig = cleaned_data.get(self.model_field_name)
        if base64_sig==None:
            error_msg = "There was an issue uploading your signature, \
                please try again."
            raise ValidationError(error_msg)
        elif not base64_sig.startswith("data:image/png;base64,"):
            error_msg = "There was an issue uploading your signature, \
                please try again."
            raise ValidationError(error_msg)
        elif base64_sig == 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAACWCAYAAABkW7XSAAAAxUlEQVR4nO3BMQEAAADCoPVPbQhfoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOA1v9QAATX68/0AAAAASUVORK5CYII=':
            error_msg = "Signature cannot be blank"
            raise ValidationError(error_msg)
        else:
            return cleaned_data

    def clean_employer_witness_name(self):
        cleaned_field = self.cleaned_data.get('employer_witness_name')
        if cleaned_field:
            return cleaned_field
        else:
            raise ValidationError('Witness name cannot be empty')

    def clean_employer_witness_nric(self):
        cleaned_field = self.cleaned_data.get('employer_witness_nric')
        if cleaned_field:
            return cleaned_field
        else:
            raise ValidationError('NRIC cannot be empty')

    def clean_fdw_witness_name(self):
        cleaned_field = self.cleaned_data.get('fdw_witness_name')
        if cleaned_field:
            return cleaned_field
        else:
            raise ValidationError('Witness name cannot be empty')

    def clean_fdw_witness_nric(self):
        cleaned_field = self.cleaned_data.get('fdw_witness_nric')
        if cleaned_field:
            return cleaned_field
        else:
            raise ValidationError('ID cannot be empty')

class VerifyUserTokenForm(forms.ModelForm):
    class Meta:
        model = EmployerDocSig
        exclude = '__all__'
        fields = ['employer_token', 'fdw_token']
    
    # Employer fields
    nric = forms.CharField()
    mobile = forms.IntegerField()

    # FDW fields
    validation_1 = forms.CharField() ############################################## TO BE UPDATED
    validation_2 = forms.IntegerField() ############################################## TO BE UPDATED

    
    def __init__(self, *args, **kwargs):
        self.is_employer = False
        self.is_fdw = False
        self.slug = kwargs.pop('slug')
        self.session = kwargs.pop('session')
        self.token_field_name = kwargs.pop('token_field_name')
        
        if self.token_field_name=='employer_token':
            self.is_employer = True
            self.object = EmployerDocSig.objects.get(employer_slug=self.slug)
            fieldset = Fieldset(
                # Legend for form
                'For security purposes, please enter the following details \
                    to verify your identify:',
                
                # Form fields - main
                'nric',
                'mobile',
            )
        elif self.token_field_name=='fdw_token':
            self.is_fdw = True
            self.object = EmployerDocSig.objects.get(fdw_slug=self.slug)
            fieldset = Fieldset(
                # Legend for form
                'For security purposes, please enter the following details \
                    to verify your identify:',
                
                # Form fields - main
                'validation_1', ############################################## TO BE UPDATED
                'validation_2', ############################################## TO BE UPDATED
            )
        
        super().__init__(*args, **kwargs)

        self.fields['nric'].label = 'NRIC'
        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            fieldset,
            Submit('submit', 'Submit')
        )

        # Make new list of all field names, then remove fields that are not
        # token_field_name.
        fields_copy = list(self.fields)
        for field in fields_copy:
            if (
                self.is_employer
                and (field=='nric' or field=='mobile')
            ):
                continue
            elif (
                self.is_fdw
                and (field=='validation_1' or field=='validation_2') ############################################## TO BE UPDATED
            ):
                continue
            elif field!=self.token_field_name:
                del self.fields[field]

    def clean(self):
        if (
            self.is_employer
                and (
                    self.cleaned_data.get('nric', '').lower() ==
                    self.object.employer_doc.employer.employer_nric.lower()
                    and
                    int(self.cleaned_data.get('mobile', 0)) ==
                    int(self.object.employer_doc.employer.employer_mobile_number)
                )
            or (
            self.is_fdw
                and ( ############################################## TO BE UPDATED
                    self.cleaned_data.get('validation_1', '') ==
                    '1'
                    and
                    int(self.cleaned_data.get('validation_2', 0)) ==
                    int(1)
                ) ############################################## TO BE UPDATED
            )
        ):
            verification_token = secrets.token_urlsafe(32)
            self.cleaned_data[self.token_field_name] = verification_token
            self.session['signature_token'] = verification_token
            self.session.set_expiry(60*10) # Session expires in 10 mins
            return self.cleaned_data
        else:
            raise ValidationError(
                'The details you entered did not match our records')
