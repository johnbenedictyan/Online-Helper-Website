# Python
import re
import secrets
import uuid

# Imports from django
from django import forms
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, Row, Column, HTML, Hidden
from crispy_forms.bootstrap import FormActions, PrependedText, StrictButton, UneditableField

# Imports from local apps
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
    JobOrder,
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
from onlinemaid.helper_functions import encrypt_string
from agency.models import AgencyEmployee
from maid.models import Maid


# Start of Forms
class EmployerForm(forms.ModelForm):
    class Meta:
        model = Employer
        exclude = [
            'nonce',
            'tag',
            'spouse_nric_nonce',
            'spouse_nric_tag',
            'sponsor_1_nric_nonce',
            'sponsor_1_nric_tag',
            'sponsor_2_nric_nonce',
            'sponsor_2_nric_tag',
            'sponsor_1_nonce_nric_spouse',
            'sponsor_1_tag_nric_spouse',
            'sponsor_1_nonce_fin_spouse',
            'sponsor_1_tag_fin_spouse',
            'sponsor_1_nonce_passport_spouse',
            'sponsor_1_tag_passport_spouse',
            'sponsor_2_nonce_nric_spouse',
            'sponsor_2_tag_nric_spouse',
            'sponsor_2_nonce_fin_spouse',
            'sponsor_2_tag_fin_spouse',
            'sponsor_2_nonce_passport_spouse',
            'sponsor_2_tag_passport_spouse',
            'joint_applicant_nonce_nric',
            'joint_applicant_tag_nric',
            'joint_applicant_nonce_nric_spouse',
            'joint_applicant_tag_nric_spouse',
            'joint_applicant_nonce_fin_spouse',
            'joint_applicant_tag_fin_spouse',
            'joint_applicant_nonce_passport_spouse',
            'joint_applicant_tag_passport_spouse',
        ]

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.user_obj = get_user_model().objects.get(pk=self.user_pk)
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.FIELD_MAXLENGTH = 20

        '''
        Decryption
        '''
        if self.instance.employer_nric and self.instance.employer_nric!=b'':
            plaintext = self.instance.get_nric_full()
            self.initial.update({'employer_nric': plaintext})
        else:
            self.initial.update({'employer_nric': ''})

        self.initial.update({'spouse_nric': self.instance.get_spouse_nric_full()})
        
        # Sponsors
        if self.instance.sponsor_1_nric and self.instance.sponsor_1_nric!=b'':
            plaintext = self.instance.get_sponsor_1_nric_full()
            self.initial.update({'sponsor_1_nric': plaintext})
        else:
            self.initial.update({'sponsor_1_nric': ''})

        if self.instance.sponsor_2_nric and self.instance.sponsor_2_nric!=b'':
            plaintext = self.instance.get_sponsor_2_nric_full()
            self.initial.update({'sponsor_2_nric': plaintext})
        else:
            self.initial.update({'sponsor_2_nric': ''})

        if self.instance.sponsor_1_nric_spouse and self.instance.sponsor_1_nric_spouse!=b'':
            plaintext = self.instance.get_sponsor_1_nric_spouse_full()
            self.initial.update({'sponsor_1_nric_spouse': plaintext})
        else:
            self.initial.update({'sponsor_1_nric_spouse': ''})

        if self.instance.sponsor_1_fin_spouse and self.instance.sponsor_1_fin_spouse!=b'':
            plaintext = self.instance.get_sponsor_1_fin_spouse_full()
            self.initial.update({'sponsor_1_fin_spouse': plaintext})
        else:
            self.initial.update({'sponsor_1_fin_spouse': ''})

        if self.instance.sponsor_1_passport_spouse and self.instance.sponsor_1_passport_spouse!=b'':
            plaintext = self.instance.get_sponsor_1_passport_spouse_full()
            self.initial.update({'sponsor_1_passport_spouse': plaintext})
        else:
            self.initial.update({'sponsor_1_passport_spouse': ''})

        if self.instance.sponsor_2_nric_spouse and self.instance.sponsor_2_nric_spouse!=b'':
            plaintext = self.instance.get_sponsor_2_nric_spouse_full()
            self.initial.update({'sponsor_2_nric_spouse': plaintext})
        else:
            self.initial.update({'sponsor_2_nric_spouse': ''})

        if self.instance.sponsor_2_fin_spouse and self.instance.sponsor_2_fin_spouse!=b'':
            plaintext = self.instance.get_sponsor_2_fin_spouse_full()
            self.initial.update({'sponsor_2_fin_spouse': plaintext})
        else:
            self.initial.update({'sponsor_2_fin_spouse': ''})

        if self.instance.sponsor_2_passport_spouse and self.instance.sponsor_2_passport_spouse!=b'':
            plaintext = self.instance.get_sponsor_2_passport_spouse_full()
            self.initial.update({'sponsor_2_passport_spouse': plaintext})
        else:
            self.initial.update({'sponsor_2_passport_spouse': ''})
        
        # Joint Applicants
        if self.instance.joint_applicant_nric and self.instance.joint_applicant_nric!=b'':
            plaintext = self.instance.get_joint_applicant_nric_full()
            self.initial.update({'joint_applicant_nric': plaintext})
        else:
            self.initial.update({'joint_applicant_nric': ''})

        if self.instance.joint_applicant_nric_spouse and self.instance.joint_applicant_nric_spouse!=b'':
            plaintext = self.instance.get_joint_applicant_nric_spouse_full()
            self.initial.update({'joint_applicant_nric_spouse': plaintext})
        else:
            self.initial.update({'joint_applicant_nric_spouse': ''})

        if self.instance.joint_applicant_fin_spouse and self.instance.joint_applicant_fin_spouse!=b'':
            plaintext = self.instance.get_joint_applicant_fin_spouse_full()
            self.initial.update({'joint_applicant_fin_spouse': plaintext})
        else:
            self.initial.update({'joint_applicant_fin_spouse': ''})

        if self.instance.joint_applicant_passport_spouse and self.instance.joint_applicant_passport_spouse!=b'':
            plaintext = self.instance.get_joint_applicant_passport_spouse_full()
            self.initial.update({'joint_applicant_passport_spouse': plaintext})
        else:
            self.initial.update({'joint_applicant_passport_spouse': ''})


        #  Remove employer_nric number from initial form display
        # self.initial.update({'employer_nric':''})
        
        self.helper = FormHelper()
        self.helper.form_class = 'employer-form'

        self.helper.layout = Layout(
            HTML(
                """
                <h3 class="mb-3">Employer Details</h3>
            """),
            Row(
                Column(
                    'employer_name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    # Note: Current position in layout helper object is self.helper.layout.fields[1][1].
                    # If position is changed, MUST update 'del self.helper.layout.fields[1][1]' line
                    # as this removes this object from the layout helper.
                    'agency_employee',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer_email',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_mobile_number',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer_nric',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_address_1',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer_address_2',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_post_code',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),

            Row(
                Column(
                    'spouse_name',
                    css_class='form-group col-md-6 employer-spouse spouse-only',
                    hidden='true',
                ),
                Column(
                    'spouse_nric',
                    css_class='form-group col-md-6 employer-spouse spouse-only',
                    hidden='true',
                ),
                css_class='form-row'
            ),
            
            # Sponsors
            Row(
                Column(
                    HTML(
                        """
                        <h5 class="doc-section-header" id="id-doc-general">Sponsors</h5>
                    """),
                    Row(
                        Column(
                            'number_of_sponsors',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            PrependedText(
                                'single_monthly_income', '$',
                                min='0', max='9999999',
                            ),
                            css_class='form-group col-md-6',
                            id='single_sponsor_income',
                        ),
                        Column(
                            PrependedText(
                                'combined_monthly_income_sponsors', '$',
                                min='0', max='9999999',
                            ),
                            css_class='form-group col-md-6 sponsor_2',
                            id='combined_sponsor_income',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_worked_in_sg',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'sponsor_1_nric',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_relationship',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'sponsor_1_name',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_gender',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            Field(
                                'sponsor_1_date_of_birth',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Sponsor 1 date of birth'
                            ),
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_nationality',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'sponsor_1_residential_status',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_mobile_number',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'sponsor_1_email',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_address_1',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'sponsor_1_address_2',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_post_code',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'sponsor_1_marital_status',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    # Sponsor 1 spouse
                    Row(
                        Column(
                            'sponsor_1_marriage_sg_registered',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_1_name_spouse',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_gender_spouse',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        Column(
                            Field(
                                'sponsor_1_date_of_birth_spouse',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Sponsor 1 spouse date of birth'
                            ),
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_nric_spouse',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_1_fin_spouse',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_passport_spouse',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        Column(
                            Field(
                                'sponsor_1_passport_date_spouse',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Sponsor 1 spouse passport expiry date',
                            ),
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_1_nationality_spouse',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_1_residential_status_spouse',
                            css_class='form-group col-md-6 spouse-1',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    # Sponsor 2
                    Row(
                        Column(
                            'sponsor_2_nric',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_relationship',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_name',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_gender',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        Column(
                            Field(
                                'sponsor_2_date_of_birth',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Sponsor 2 date of birth',
                            ),
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_nationality',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_residential_status',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_mobile_number',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_email',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_address_1',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_address_2',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_post_code',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_marital_status',
                            css_class='form-group col-md-6 sponsor-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    # Sponsor 2 spouse
                    Row(
                        Column(
                            'sponsor_2_marriage_sg_registered',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_name_spouse',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_gender_spouse',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        Column(
                            Field(
                                'sponsor_2_date_of_birth_spouse',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Sponsor 2 date of birth',
                            ),
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_nric_spouse',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_fin_spouse',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            'sponsor_2_passport_spouse',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        Column(
                            Field(
                                'sponsor_2_passport_date_spouse',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Sponsor 2 spouse passport expiry date',
                            ),
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'sponsor_2_nationality_spouse',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        Column(
                            'sponsor_2_residential_status_spouse',
                            css_class='form-group col-md-6 spouse-2',
                            hidden='true',
                        ),
                        css_class='form-row',
                    ),
                    id='sponsors',
                )
            ),

            # Joint Applicants
            Row(
                Column(
                    PrependedText(
                        'combined_monthly_income_joint_applicants', '$',
                        min='0', max='9999999',
                    ),
                    css_class='form-group col-md-6',
                ),
                Column(
                    'worked_in_sg',
                    css_class='form-group col-md-6',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_relationship',
                    css_class='form-group col-md-6',
                ),
                Column(
                    'joint_applicant_name',
                    css_class='form-group col-md-6',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_nric',
                    css_class='form-group col-md-4',
                ),
                Column(
                    'joint_applicant_gender',
                    css_class='form-group col-md-4',
                ),
                Column(
                    Field(
                        'joint_applicant_date_of_birth',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Joint applicant date of birth'
                    ),
                    css_class='form-group col-md-4',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_nationality',
                    css_class='form-group col-md-6',
                ),
                Column(
                    'joint_applicant_residential_status',
                    css_class='form-group col-md-6',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_address_1',
                    css_class='form-group col-md-6',
                ),
                Column(
                    'joint_applicant_address_2',
                    css_class='form-group col-md-6',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_post_code',
                    css_class='form-group col-md-6',
                ),
                Column(
                    'joint_applicant_marital_status',
                    css_class='form-group col-md-6',
                ),
                css_class='form-row',
            ),
            # Joint applicant spouse
            Row(
                Column(
                    'joint_applicant_marriage_sg_registered',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                Column(
                    'joint_applicant_name_spouse',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_gender_spouse',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                Column(
                    Field(
                        'joint_applicant_date_of_birth_spouse',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Joint applicant spouse date of birth'
                    ),
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_nric_spouse',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                Column(
                    'joint_applicant_fin_spouse',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_passport_spouse',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                Column(
                    Field(
                        'joint_applicant_passport_date_spouse',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Joint applicant spouse passport expiry date',
                    ),
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                css_class='form-row',
            ),
            Row(
                Column(
                    'joint_applicant_nationality_spouse',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                Column(
                    'joint_applicant_residential_status_spouse',
                    css_class='form-group col-md-6 spouse-1',
                    hidden='true',
                ),
                css_class='form-row',
            ),

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

        if self.agency_user_group==AG_OWNERS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_owner.agency
                )
            )
        elif self.agency_user_group==AG_ADMINS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_employee.agency
                )
            )
        elif self.agency_user_group==AG_MANAGERS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    branch=self.user_obj.agency_employee.branch
                )
            )
        else:
            del self.helper.layout.fields[1][1] # Remember to make this match the position of the 'agency_employee' field in the layout helper object above
            del self.fields['agency_employee']
    
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

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.nonce, self.instance.tag = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        
        return ciphertext

    # Employer Spouse
    def clean_spouse_nric(self):
        cleaned_field = self.cleaned_data.get('spouse_nric')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.spouse_nric_nonce, self.instance.spouse_nric_tag = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    # Sponsors
    def clean_sponsor_1_nric(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_nric')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_1_nric_nonce, self.instance.sponsor_1_nric_tag = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_sponsor_2_nric(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_nric')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_2_nric_nonce, self.instance.sponsor_2_nric_tag = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_sponsor_1_nric_spouse(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_nric_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_1_nonce_nric_spouse, self.instance.sponsor_1_tag_nric_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_sponsor_1_fin_spouse(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_fin_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_1_nonce_fin_spouse, self.instance.sponsor_1_tag_fin_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_sponsor_1_passport_spouse(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_passport_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_1_nonce_passport_spouse, self.instance.sponsor_1_tag_passport_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_sponsor_2_nric_spouse(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_nric_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_2_nonce_nric_spouse, self.instance.sponsor_2_tag_nric_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_sponsor_2_fin_spouse(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_fin_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_2_nonce_fin_spouse, self.instance.sponsor_2_tag_fin_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_sponsor_2_passport_spouse(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_passport_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.sponsor_2_nonce_passport_spouse, self.instance.sponsor_2_tag_passport_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    # Joint Applicants
    def clean_joint_applicant_nric(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_nric')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.joint_applicant_nonce_nric, self.instance.joint_applicant_tag_nric = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_joint_applicant_nric_spouse(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_nric_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.joint_applicant_nonce_nric_spouse, self.instance.joint_applicant_tag_nric_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_joint_applicant_fin_spouse(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_fin_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.joint_applicant_nonce_fin_spouse, self.instance.joint_applicant_tag_fin_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

    def clean_joint_applicant_passport_spouse(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_passport_spouse')

        if not isinstance(cleaned_field, str):
            raise ValidationError('Must be a string')

        if not re.match('^[A-Za-z0-9]*$', cleaned_field):
            raise ValidationError('Can only enter letters or numbers')

        if len(cleaned_field)>self.FIELD_MAXLENGTH:
            raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

        # Encryption
        ciphertext, self.instance.joint_applicant_nonce_passport_spouse, self.instance.joint_applicant_tag_passport_spouse = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )
        return ciphertext

class EmployerDocForm(forms.ModelForm):
    class Meta:
        model = EmployerDoc
        exclude = ['employer']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.FIELD_MAXLENGTH = 20

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
                <h3 class="mb-3">Documentation Form</h3>
                <h5 class="doc-section-header" id="id-doc-general">General</h5>
            """),
            # General
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
                    Field(
                        'agreement_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Agreement date'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'application_scheme',
                    css_class='form-group col-md-6',
                    id='application-scheme',
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'monthly_combined_income',
                    css_class='form-group col-md-6 employer-spouse employer-only',
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
                    PrependedText(
                        'b1_service_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'b2a_work_permit_application_collection', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2b_medical_examination_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'b2c_security_bond_accident_insurance', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2d_indemnity_policy_reimbursement', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'b2e_home_service', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2f_counselling', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'b2g_sip', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'b2h_replacement_months',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'b2h_replacement_cost', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2i_work_permit_renewal', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2j1_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2j1_other_services_fee', '$',
                        min='0', max='1000',
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
                    PrependedText(
                        'b2j2_other_services_fee', '$',
                        min='0', max='1000',
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
                    PrependedText(
                        'b2j3_other_services_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'b3_agency_fee', '$',
                        min='0', max='10000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b3_fdw_loan', '$',
                        min='0', max='10000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'ca_deposit', '$',
                        min='0', max='10000',
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
                    PrependedText(
                        'b4_loan_transferred', '$',
                        min='0', max='1000',
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
                #     PrependedText(
                #         '', '$',
                #         min='0', max='1000',
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
                    PrependedText(
                        'c3_4_no_replacement_refund', '$',
                        min='0', max='1000',
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
                    PrependedText(
                        'c5_1_1_failed_deployment_refund', '$',
                        min='0', max='1000',
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
                    PrependedText(
                        'c5_1_2_before_fdw_arrives_charge', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'c5_1_2_after_fdw_arrives_charge', '$',
                        min='0', max='1000',
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
                    PrependedText(
                        'c6_4_per_day_food_accommodation_cost', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'c6_6_per_session_counselling_cost', '$',
                        min='0', max='1000',
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
                    PrependedText(
                        'c3_1_fdw_salary', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
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
            # Safety Agreement
            HTML(
                """
                <h5 class="doc-section-header" id="id-doc-safety-agreement">Safety Agreement</h5>
            """),
            Row(
                Column(
                    'residential_dwelling_type',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'fdw_clean_window_exterior',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'window_exterior_location',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'grilles_installed_require_cleaning',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'adult_supervision',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'verifiy_employer_understands_window_cleaning',
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

    def clean(self):
        window_exterior_location_verbose_name = EmployerDoc._meta.get_field('window_exterior_location').verbose_name
        window_exterior_error_msg = window_exterior_location_verbose_name + ' field cannot be blank'
        if self.cleaned_data.get('fdw_clean_window_exterior') and not self.cleaned_data.get('window_exterior_location'):
            self.add_error(
                'window_exterior_location',
                ValidationError(
                    window_exterior_error_msg,
                    code= 'error_window_exterior_location',
                    params= {
                        'window_exterior_location': window_exterior_location_verbose_name
                    },
                )
            )
        
        grilles_installed_verbose_name = EmployerDoc._meta.get_field('grilles_installed_require_cleaning').verbose_name
        grilles_installed_error_msg = grilles_installed_verbose_name + ' field cannot be blank'
        if self.cleaned_data.get('window_exterior_location')=='OTHER' and self.cleaned_data.get('grilles_installed_require_cleaning')==None:
            self.add_error(
                'grilles_installed_require_cleaning',
                ValidationError(
                    grilles_installed_error_msg,
                    code= 'error_grilles_installed_require_cleaning',
                    params= {
                        'grilles_installed_require_cleaning': grilles_installed_verbose_name
                    },
                )
            )
        
        adult_supervision_verbose_name = EmployerDoc._meta.get_field('adult_supervision').verbose_name
        adult_supervision_error_msg = 'Adult supervision is required if grilles installed on windows are to be cleaned by FDW'
        if self.cleaned_data.get('grilles_installed_require_cleaning') and not self.cleaned_data.get('adult_supervision'):
            self.add_error(
                'adult_supervision',
                ValidationError(
                    adult_supervision_error_msg,
                    code= 'error_adult_supervision',
                    params= {
                        'adult_supervision': adult_supervision_verbose_name
                    },
                )
            )
        
        verifiy_employer_understands_verbose_name = EmployerDoc._meta.get_field('verifiy_employer_understands_window_cleaning').verbose_name
        verifiy_employer_understands_error_msg = 'This field must correspond with previous fields'
        if (
            (not self.cleaned_data.get('fdw_clean_window_exterior') and not self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==1)
            or
            (self.cleaned_data.get('window_exterior_location')=='GROUND' and not self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==2)
            or
            (self.cleaned_data.get('window_exterior_location')=='COMMON' and not self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==3)
            or
            (self.cleaned_data.get('window_exterior_location')=='OTHER' and not self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==4)
            or
            (self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==1 and self.cleaned_data.get('fdw_clean_window_exterior'))
            or
            (self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==2 and not self.cleaned_data.get('window_exterior_location')=='GROUND')
            or
            (self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==3 and not self.cleaned_data.get('window_exterior_location')=='COMMON')
            or
            (self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==4 and not self.cleaned_data.get('window_exterior_location')=='OTHER')
            or
            (self.cleaned_data.get('verifiy_employer_understands_window_cleaning')==4 and self.cleaned_data.get('window_exterior_location')=='OTHER' and not self.cleaned_data.get('grilles_installed_require_cleaning'))
        ):
            self.add_error(
                'verifiy_employer_understands_window_cleaning',
                ValidationError(
                    verifiy_employer_understands_error_msg,
                    code= 'error_verifiy_employer_understands',
                    params= {
                        'verifiy_employer_understands_window_cleaning': verifiy_employer_understands_verbose_name
                    },
                )
            )
        
        return self.cleaned_data

class EmployerDocSigSlugForm(forms.ModelForm):
    class Meta:
        model = EmployerDocSig
        fields = ['employer_slug', 'fdw_slug']
        labels = {
            'employer_slug': _('Employer signature URL'),
            'fdw_slug': _('FDW signature URL'),
        }

    def __init__(self, *args, **kwargs):
        self.model_field_name = kwargs.pop('model_field_name')
        self.form_fields = kwargs.pop('form_fields')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout()
        
        # Insert full URL path to signature token URL
        current_site = Site.objects.get_current()
        self.initial.update({
            self.model_field_name: current_site.domain + reverse(
                'token_verification_' + self.model_field_name[:-5] + '_route',
                kwargs={'slug':self.initial.get(self.model_field_name)}
            )
        })
        
        # Make copy of all field names, then remove fields that are not in self.form_fields
        fields_copy = list(self.fields)
        for field in fields_copy:
            if field!=self.model_field_name:
                del self.fields[field]
        
        self.helper.layout.append(
            HTML('''
                <h5>Unique URL</h5>
            ''')
        )
        self.helper.layout.append(
            UneditableField(
                self.model_field_name,
                id='copy-id',
                css_class='col',
            )
        )
        self.helper.layout.append(
            StrictButton(
                '<i class="fas fa-copy"></i>',
                id="copy-button",
                css_class="btn btn-secondary",
            )
        )
        
        # Workaround for validation always failing due to missing field.
        # This duplicates the input field, meaning that there are 2 HTML input fields with same name.
        # Without this duplicate, the form validation fails, saying that first field is required.
        self.helper.layout.append(
            Hidden(self.model_field_name, 'null',)
        )

        # Submitting form will regen new slug
        self.helper.layout.append(
            Submit('submit', 'Renew URL')
        )

    def clean_employer_slug(self):
        return uuid.uuid4()

    def clean_fdw_slug(self):
        return uuid.uuid4()

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
            HTML('''
                <h3>FDW Status</h3>
                '''
            ),
            Row(
                Column(
                    Field(
                        'fdw_work_commencement_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='FDW work commencement date'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field(
                        'ipa_approval_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='IPA approval date'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Field(
                        'arrival_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='FDW arrival date'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field(
                        'security_bond_approval_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Security bond approval date'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Field(
                        'thumb_print_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Thumb print date'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field(
                        'sip_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Settling in Programme (SIP) date'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Field(
                        'work_permit_no',
                        type='text',
                        placeholder='Work permit number'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'is_deployed',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Submit('submit', 'Submit')
        )

    def clean(self):
        error_msg = _('%(field)s field must not be empty.')
        
        def check_field_not_empty(field):
            if not self.cleaned_data.get(field):
                self.add_error(
                    field,
                    ValidationError(
                        error_msg,
                        code= 'error_' + field,
                        params= {
                            'field': EmployerDocMaidStatus._meta.get_field(
                                field).verbose_name
                        },
                    )
                )

        if self.cleaned_data.get('is_deployed'):
            for field in self.fields:
                if field!='work_permit_no' and field!='is_deployed':
                    check_field_not_empty(field)

        return self.cleaned_data

class EmployerDocMaidDeploymentForm(forms.ModelForm):
    class Meta:
        model = EmployerDocMaidStatus
        fields = ['is_deployed']

class EmployerPaymentTransactionForm(forms.ModelForm):
    class Meta:
        model = EmployerPaymentTransaction
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'employer-doc-form'
        self.helper.layout = Layout(
            Row(
                Column(
                    Field(
                        'transaction_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Transaction date'
                    ),
                    css_class='form-group col-md-4'
                ),
                Column(
                    PrependedText(
                        'amount', '$',
                        min='0', max='10000',
                    ),
                    css_class='form-group col-md-4'
                ),
                Column(
                    'transaction_type',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
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
            Field(
                'job_order_pdf',
            ),
            Submit('submit', 'Submit')
        )

# class EmployerSponsorForm(forms.ModelForm):
#     class Meta:
#         model = EmployerSponsor
#         exclude = ['employer_doc',
#             'sponsor_1_nric_nonce',
#             'sponsor_1_nric_tag',
#             'sponsor_2_nric_nonce',
#             'sponsor_2_nric_tag',
#             'sponsor_1_nonce_nric_spouse',
#             'sponsor_1_tag_nric_spouse',
#             'sponsor_1_nonce_fin_spouse',
#             'sponsor_1_tag_fin_spouse',
#             'sponsor_1_nonce_passport_spouse',
#             'sponsor_1_tag_passport_spouse',
#             'sponsor_2_nonce_nric_spouse',
#             'sponsor_2_tag_nric_spouse',
#             'sponsor_2_nonce_fin_spouse',
#             'sponsor_2_tag_fin_spouse',
#             'sponsor_2_nonce_passport_spouse',
#             'sponsor_2_tag_passport_spouse',
#         ]

#     def __init__(self, *args, **kwargs):
#         self.user_pk = kwargs.pop('user_pk')
#         self.agency_user_group = kwargs.pop('agency_user_group')
#         super().__init__(*args, **kwargs)

#         self.FIELD_MAXLENGTH = 20

#         '''
#         Decryption
#         '''
#         if self.instance.sponsor_1_nric and self.instance.sponsor_1_nric!=b'':
#             plaintext = self.instance.get_sponsor_1_nric_full()
#             self.initial.update({'sponsor_1_nric': plaintext})
#         else:
#             self.initial.update({'sponsor_1_nric': ''})

#         if self.instance.sponsor_2_nric and self.instance.sponsor_2_nric!=b'':
#             plaintext = self.instance.get_sponsor_2_nric_full()
#             self.initial.update({'sponsor_2_nric': plaintext})
#         else:
#             self.initial.update({'sponsor_2_nric': ''})

#         if self.instance.sponsor_1_nric_spouse and self.instance.sponsor_1_nric_spouse!=b'':
#             plaintext = self.instance.get_sponsor_1_nric_spouse_full()
#             self.initial.update({'sponsor_1_nric_spouse': plaintext})
#         else:
#             self.initial.update({'sponsor_1_nric_spouse': ''})

#         if self.instance.sponsor_1_fin_spouse and self.instance.sponsor_1_fin_spouse!=b'':
#             plaintext = self.instance.get_sponsor_1_fin_spouse_full()
#             self.initial.update({'sponsor_1_fin_spouse': plaintext})
#         else:
#             self.initial.update({'sponsor_1_fin_spouse': ''})

#         if self.instance.sponsor_1_passport_spouse and self.instance.sponsor_1_passport_spouse!=b'':
#             plaintext = self.instance.get_sponsor_1_passport_spouse_full()
#             self.initial.update({'sponsor_1_passport_spouse': plaintext})
#         else:
#             self.initial.update({'sponsor_1_passport_spouse': ''})

#         if self.instance.sponsor_2_nric_spouse and self.instance.sponsor_2_nric_spouse!=b'':
#             plaintext = self.instance.get_sponsor_2_nric_spouse_full()
#             self.initial.update({'sponsor_2_nric_spouse': plaintext})
#         else:
#             self.initial.update({'sponsor_2_nric_spouse': ''})

#         if self.instance.sponsor_2_fin_spouse and self.instance.sponsor_2_fin_spouse!=b'':
#             plaintext = self.instance.get_sponsor_2_fin_spouse_full()
#             self.initial.update({'sponsor_2_fin_spouse': plaintext})
#         else:
#             self.initial.update({'sponsor_2_fin_spouse': ''})

#         if self.instance.sponsor_2_passport_spouse and self.instance.sponsor_2_passport_spouse!=b'':
#             plaintext = self.instance.get_sponsor_2_passport_spouse_full()
#             self.initial.update({'sponsor_2_passport_spouse': plaintext})
#         else:
#             self.initial.update({'sponsor_2_passport_spouse': ''})

#         self.helper = FormHelper()
#         self.helper.form_class = 'employer-doc-form'
#         self.helper.layout = Layout(
#             Row(
#                 Column(
#                     'number_of_sponsors',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     PrependedText(
#                         'single_monthly_income', '$',
#                         min='0', max='9999999',
#                     ),
#                     css_class='form-group col-md-6',
#                     id='single_sponsor_income',
#                 ),
#                 Column(
#                     PrependedText(
#                         'combined_monthly_income', '$',
#                         min='0', max='9999999',
#                     ),
#                     css_class='form-group col-md-6 sponsor_2',
#                     id='combined_sponsor_income',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_worked_in_sg',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'sponsor_1_nric',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_relationship',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'sponsor_1_name',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_gender',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     Field(
#                         'sponsor_1_date_of_birth',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Sponsor 1 date of birth'
#                     ),
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_nationality',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'sponsor_1_residential_status',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_mobile_number',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'sponsor_1_email',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_address_1',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'sponsor_1_address_2',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_post_code',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'sponsor_1_marital_status',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             # Sponsor 1 spouse
#             Row(
#                 Column(
#                     'sponsor_1_marriage_sg_registered',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_1_name_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_gender_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     Field(
#                         'sponsor_1_date_of_birth_spouse',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Sponsor 1 spouse date of birth'
#                     ),
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_nric_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_1_fin_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_passport_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     Field(
#                         'sponsor_1_passport_date_spouse',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Sponsor 1 spouse passport expiry date',
#                     ),
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_1_nationality_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_1_residential_status_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             # Sponsor 2
#             Row(
#                 Column(
#                     'sponsor_2_nric',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_relationship',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_name',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_gender',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     Field(
#                         'sponsor_2_date_of_birth',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Sponsor 2 date of birth',
#                     ),
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_nationality',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_residential_status',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_mobile_number',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_email',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_address_1',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_address_2',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_post_code',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_marital_status',
#                     css_class='form-group col-md-6 sponsor-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             # Sponsor 2 spouse
#             Row(
#                 Column(
#                     'sponsor_2_marriage_sg_registered',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_name_spouse',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_gender_spouse',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     Field(
#                         'sponsor_2_date_of_birth_spouse',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Sponsor 2 date of birth',
#                     ),
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_nric_spouse',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_fin_spouse',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_passport_spouse',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     Field(
#                         'sponsor_2_passport_date_spouse',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Sponsor 2 spouse passport expiry date',
#                     ),
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'sponsor_2_nationality_spouse',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 Column(
#                     'sponsor_2_residential_status_spouse',
#                     css_class='form-group col-md-6 spouse-2',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Submit('submit', 'Submit')
#         )

#     def clean_sponsor_1_nric(self):
#         cleaned_field = self.cleaned_data.get('sponsor_1_nric')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_1_nric_nonce, self.instance.sponsor_1_nric_tag = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_sponsor_2_nric(self):
#         cleaned_field = self.cleaned_data.get('sponsor_2_nric')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_2_nric_nonce, self.instance.sponsor_2_nric_tag = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_sponsor_1_nric_spouse(self):
#         cleaned_field = self.cleaned_data.get('sponsor_1_nric_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_1_nonce_nric_spouse, self.instance.sponsor_1_tag_nric_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_sponsor_1_fin_spouse(self):
#         cleaned_field = self.cleaned_data.get('sponsor_1_fin_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_1_nonce_fin_spouse, self.instance.sponsor_1_tag_fin_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_sponsor_1_passport_spouse(self):
#         cleaned_field = self.cleaned_data.get('sponsor_1_passport_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_1_nonce_passport_spouse, self.instance.sponsor_1_tag_passport_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_sponsor_2_nric_spouse(self):
#         cleaned_field = self.cleaned_data.get('sponsor_2_nric_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_2_nonce_nric_spouse, self.instance.sponsor_2_tag_nric_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_sponsor_2_fin_spouse(self):
#         cleaned_field = self.cleaned_data.get('sponsor_2_fin_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_2_nonce_fin_spouse, self.instance.sponsor_2_tag_fin_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_sponsor_2_passport_spouse(self):
#         cleaned_field = self.cleaned_data.get('sponsor_2_passport_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.sponsor_2_nonce_passport_spouse, self.instance.sponsor_2_tag_passport_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

# class EmployerJointApplicantForm(forms.ModelForm):
#     class Meta:
#         model = EmployerJointApplicant
#         exclude = [
#             'employer_doc',
#             'joint_applicant_nonce_nric',
#             'joint_applicant_tag_nric',
#             'joint_applicant_nonce_nric_spouse',
#             'joint_applicant_tag_nric_spouse',
#             'joint_applicant_nonce_fin_spouse',
#             'joint_applicant_tag_fin_spouse',
#             'joint_applicant_nonce_passport_spouse',
#             'joint_applicant_tag_passport_spouse',
#         ]

#     def __init__(self, *args, **kwargs):
#         self.user_pk = kwargs.pop('user_pk')
#         self.agency_user_group = kwargs.pop('agency_user_group')
#         super().__init__(*args, **kwargs)

#         self.FIELD_MAXLENGTH = 20

#         '''
#         Decryption
#         '''
#         if self.instance.joint_applicant_nric and self.instance.joint_applicant_nric!=b'':
#             plaintext = self.instance.get_joint_applicant_nric_full()
#             self.initial.update({'joint_applicant_nric': plaintext})
#         else:
#             self.initial.update({'joint_applicant_nric': ''})

#         if self.instance.joint_applicant_nric_spouse and self.instance.joint_applicant_nric_spouse!=b'':
#             plaintext = self.instance.get_joint_applicant_nric_spouse_full()
#             self.initial.update({'joint_applicant_nric_spouse': plaintext})
#         else:
#             self.initial.update({'joint_applicant_nric_spouse': ''})

#         if self.instance.joint_applicant_fin_spouse and self.instance.joint_applicant_fin_spouse!=b'':
#             plaintext = self.instance.get_joint_applicant_fin_spouse_full()
#             self.initial.update({'joint_applicant_fin_spouse': plaintext})
#         else:
#             self.initial.update({'joint_applicant_fin_spouse': ''})

#         if self.instance.joint_applicant_passport_spouse and self.instance.joint_applicant_passport_spouse!=b'':
#             plaintext = self.instance.get_joint_applicant_passport_spouse_full()
#             self.initial.update({'joint_applicant_passport_spouse': plaintext})
#         else:
#             self.initial.update({'joint_applicant_passport_spouse': ''})

#         self.helper = FormHelper()
#         self.helper.form_class = 'employer-doc-form'
#         self.helper.layout = Layout(
#             Row(
#                 Column(
#                     PrependedText(
#                         'combined_monthly_income', '$',
#                         min='0', max='9999999',
#                     ),
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'worked_in_sg',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_relationship',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'joint_applicant_name',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_nric',
#                     css_class='form-group col-md-4',
#                 ),
#                 Column(
#                     'joint_applicant_gender',
#                     css_class='form-group col-md-4',
#                 ),
#                 Column(
#                     Field(
#                         'joint_applicant_date_of_birth',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Joint applicant date of birth'
#                     ),
#                     css_class='form-group col-md-4',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_nationality',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'joint_applicant_residential_status',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_address_1',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'joint_applicant_address_2',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_post_code',
#                     css_class='form-group col-md-6',
#                 ),
#                 Column(
#                     'joint_applicant_marital_status',
#                     css_class='form-group col-md-6',
#                 ),
#                 css_class='form-row',
#             ),
#             # Joint applicant spouse
#             Row(
#                 Column(
#                     'joint_applicant_marriage_sg_registered',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     'joint_applicant_name_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_gender_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     Field(
#                         'joint_applicant_date_of_birth_spouse',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Joint applicant spouse date of birth'
#                     ),
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_nric_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     'joint_applicant_fin_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_passport_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     Field(
#                         'joint_applicant_passport_date_spouse',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Joint applicant spouse passport expiry date',
#                     ),
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Row(
#                 Column(
#                     'joint_applicant_nationality_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 Column(
#                     'joint_applicant_residential_status_spouse',
#                     css_class='form-group col-md-6 spouse-1',
#                     hidden='true',
#                 ),
#                 css_class='form-row',
#             ),
#             Submit('submit', 'Submit')
#         )

#     def clean_joint_applicant_nric(self):
#         cleaned_field = self.cleaned_data.get('joint_applicant_nric')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.joint_applicant_nonce_nric, self.instance.joint_applicant_tag_nric = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_joint_applicant_nric_spouse(self):
#         cleaned_field = self.cleaned_data.get('joint_applicant_nric_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.joint_applicant_nonce_nric_spouse, self.instance.joint_applicant_tag_nric_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_joint_applicant_fin_spouse(self):
#         cleaned_field = self.cleaned_data.get('joint_applicant_fin_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.joint_applicant_nonce_fin_spouse, self.instance.joint_applicant_tag_fin_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

#     def clean_joint_applicant_passport_spouse(self):
#         cleaned_field = self.cleaned_data.get('joint_applicant_passport_spouse')

#         if not isinstance(cleaned_field, str):
#             raise ValidationError('Must be a string')

#         if not re.match('^[A-Za-z0-9]*$', cleaned_field):
#             raise ValidationError('Can only enter letters or numbers')

#         if len(cleaned_field)>self.FIELD_MAXLENGTH:
#             raise ValidationError(f'Must not exceed {self.FIELD_MAXLENGTH} characters')

#         # Encryption
#         ciphertext, self.instance.joint_applicant_nonce_passport_spouse, self.instance.joint_applicant_tag_passport_spouse = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )
#         return ciphertext

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
                        Column(field, css_class='form-group col-md-6'),
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
                    StrictButton("Clear", onclick="signaturePad.clear()", css_class="btn btn-secondary"),
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
        elif base64_sig == 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAACWCAYAAABkW7XSAAAEYklEQVR4Xu3UAQkAAAwCwdm/9HI83BLIOdw5AgQIRAQWySkmAQIEzmB5AgIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlAABg+UHCBDICBisTFWCEiBgsPwAAQIZAYOVqUpQAgQMlh8gQCAjYLAyVQlKgIDB8gMECGQEDFamKkEJEDBYfoAAgYyAwcpUJSgBAgbLDxAgkBEwWJmqBCVAwGD5AQIEMgIGK1OVoAQIGCw/QIBARsBgZaoSlACBB1YxAJfjJb2jAAAAAElFTkSuQmCC':
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
        input_nric = self.cleaned_data.get('nric', '')
        plaintext = self.object.employer_doc.employer.get_nric_full()
        if (
            self.is_employer
                and (
                    input_nric.lower() ==
                    plaintext.lower()
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
            self.session.set_expiry(60*30) # Session expires in 30 mins
            return self.cleaned_data
        else:
            raise ValidationError(
                'The details you entered did not match our records')
