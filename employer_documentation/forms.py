# Python
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
from . import models
from onlinemaid import constants as om_constants
from onlinemaid import helper_functions
from agency.models import AgencyEmployee
from maid.models import Maid


# Start of Forms
class EmployerForm(forms.ModelForm):
    class Meta:
        model = models.Employer
        exclude = [
            'employer_nric_nonce',
            'employer_nric_tag',
            'employer_fin_nonce',
            'employer_fin_tag',
            'employer_passport_nonce',
            'employer_passport_tag',
            'spouse_nric_nonce',
            'spouse_nric_tag',
            'spouse_fin_nonce',
            'spouse_fin_tag',
            'spouse_passport_nonce',
            'spouse_passport_tag',
        ]

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.user_obj = get_user_model().objects.get(pk=self.user_pk)
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        # Decryption
        self.initial.update({'employer_nric_num': self.instance.get_employer_nric_full()})
        self.initial.update({'employer_fin_num': self.instance.get_employer_fin()})
        self.initial.update({'employer_passport_num': self.instance.get_employer_passport()})
        self.initial.update({'spouse_nric_num': self.instance.get_spouse_nric_full()})
        self.initial.update({'spouse_fin_num': self.instance.get_spouse_fin()})
        self.initial.update({'spouse_passport_num': self.instance.get_spouse_passport()})
        
        # CrispyForm Helper
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(
                """
                <h3 class="mb-3">Employer Form</h3>
            """),
            Row(
                Column(
                    'applicant_type',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'household_details_required',
                    css_class='form-group col-md-6',
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    # Note: Current position in layout helper object is self.helper.layout.fields[1][1].
                    # If position is changed, MUST update 'del self.helper.layout.fields[1][1]' line
                    # as this removes this object from the layout helper.
                    'agency_employee',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            
            # Employer Details
            HTML(
                """
                <h5 class="my-3">Employer Information</h5>
            """),
            Row(
                Column(
                    'employer_name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_gender',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer_mobile_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_home_number',
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
                    'employer_date_of_birth',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_nationality',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer_residential_status',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_nric_num',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer_fin_num',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_passport_num',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer_passport_date',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_marital_status',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),

            # Spouse's Information
            Row(
                Column(
                    HTML(
                        """
                        <h5 class="my-3">Spouse Information</h5>
                    """),
                    Row(
                        Column(
                            'spouse_name',
                            css_class='form-group col-md-6 employer-spouse spouse-only',
                            hidden='true',
                        ),
                        Column(
                            'spouse_gender',
                            css_class='form-group col-md-6 employer-spouse spouse-only',
                            hidden='true',
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            'spouse_date_of_birth',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'spouse_nationality',
                            css_class='form-group col-md-6'
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            'spouse_residential_status',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'spouse_nric_num',
                            css_class='form-group col-md-6'
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            'spouse_fin_num',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'spouse_passport_num',
                            css_class='form-group col-md-6'
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            'spouse_passport_date',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'employer_marriage_sg_registered',
                            css_class='form-group col-md-6'
                        ),
                        css_class='form-row'
                    ),
                ),
                id='spouse-section',
            ),

            # # Income Details
            # Row(
            #     Column(
            #         HTML(
            #             """
            #             <h5 class="my-3">Income Details</h5>
            #         """),
            #         Row(
            #             Column(
            #                 'monthly_income',
            #                 css_class='form-group col-md-6',
            #             ),
            #             css_class='form-row'
            #         ),
            #     ),
            #     id='household-section',
            # ),

            # # Household Details
            # Row(
            #     Column(
            #         HTML(
            #             """
            #             <h5 class="my-3">Household Details</h5>
            #         """),
            #         Row(
            #             Column(
            #                 'household_name',
            #                 css_class='form-group col-md-6',
            #             ),
            #             Column(
            #                 'household_id_type',
            #                 css_class='form-group col-md-6'
            #             ),
            #             css_class='form-row'
            #         ),
            #         Row(
            #             Column(
            #                 'household_id_num',
            #                 css_class='form-group col-md-6'
            #             ),
            #             Column(
            #                 'household_date_of_birth',
            #                 css_class='form-group col-md-6',
            #             ),
            #             css_class='form-row'
            #         ),
            #         Row(
            #             Column(
            #                 'household_relationship',
            #                 css_class='form-group col-md-6'
            #             ),
            #             css_class='form-row'
            #         ),
            #     ),
            #     id='household-section',
            # ),

            # Submit
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

        if self.agency_user_group==om_constants.AG_OWNERS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_owner.agency
                )
            )
        elif self.agency_user_group==om_constants.AG_ADMINS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_employee.agency
                )
            )
        elif self.agency_user_group==om_constants.AG_MANAGERS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    branch=self.user_obj.agency_employee.branch
                )
            )
        else:
            del self.helper.layout.fields[2][1] # Remember to make this match the position of the 'agency_employee' field in the layout helper object above
            del self.fields['agency_employee']
    
    def check_queryset(self, queryset, error_msg):
        for employer_obj in queryset:
            if not employer_obj==self.instance:
                # Check if it belongs to current user's agency
                if self.agency_user_group==om_constants.AG_OWNERS:
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
            employer_queryset = models.Employer.objects.filter(
                employer_email=cleaned_field
            )
        except models.Employer.DoesNotExist:
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
            employer_queryset = models.Employer.objects.filter(
                employer_mobile_number=cleaned_field
            )
        except models.Employer.DoesNotExist:
            # If no entries for employer_mobile_number, then no further checks
            return cleaned_field
        else:
            self.check_queryset(
                employer_queryset,
                'An employer with this mobile number already exists in your \
                    agency'
            )
        return cleaned_field

    def clean_employer_nric_num(self):
        cleaned_field = self.cleaned_data.get('employer_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.employer_nric_nonce, self.instance.employer_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_employer_fin_num(self):
        cleaned_field = self.cleaned_data.get('employer_fin_num')
        error_msg = helper_functions.validate_fin(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.employer_fin_nonce, self.instance.employer_fin_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_employer_passport_num(self):
        cleaned_field = self.cleaned_data.get('employer_passport_num')
        error_msg = helper_functions.validate_passport(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.employer_passport_nonce, self.instance.employer_passport_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_spouse_nric_num(self):
        cleaned_field = self.cleaned_data.get('spouse_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.spouse_nric_nonce, self.instance.spouse_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_spouse_fin_num(self):
        cleaned_field = self.cleaned_data.get('spouse_fin_num')
        error_msg = helper_functions.validate_fin(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.spouse_fin_nonce, self.instance.spouse_fin_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_spouse_passport_num(self):
        cleaned_field = self.cleaned_data.get('spouse_passport_num')
        error_msg = helper_functions.validate_passport(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.spouse_passport_nonce, self.instance.spouse_passport_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

class EmployerSponsorForm(forms.ModelForm):
    class Meta:
        model = models.EmployerSponsor
        exclude = [
            'employer',
            'sponsor_1_nric_nonce',
            'sponsor_1_nric_tag',
            'sponsor_1_spouse_nric_nonce',
            'sponsor_1_spouse_nric_tag',
            'sponsor_1_spouse_fin_nonce',
            'sponsor_1_spouse_fin_tag',
            'sponsor_1_spouse_passport_nonce',
            'sponsor_1_spouse_passport_tag',
            'sponsor_2_nric_nonce',
            'sponsor_2_nric_tag',
            'sponsor_2_spouse_nric_nonce',
            'sponsor_2_spouse_nric_tag',
            'sponsor_2_spouse_fin_nonce',
            'sponsor_2_spouse_fin_tag',
            'sponsor_2_spouse_passport_nonce',
            'sponsor_2_spouse_passport_tag',
        ]

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.initial.update({'sponsor_1_nric_num': self.instance.get_sponsor_1_nric_full()})
        self.initial.update({'sponsor_1_spouse_nric_num': self.instance.get_sponsor_1_spouse_nric_full()})
        self.initial.update({'sponsor_1_spouse_fin_num': self.instance.get_sponsor_1_spouse_fin_full()})
        self.initial.update({'sponsor_1_spouse_passport_num': self.instance.get_sponsor_1_spouse_passport_full()})
        
        self.initial.update({'sponsor_2_nric_num': self.instance.get_sponsor_2_nric_full()})
        self.initial.update({'sponsor_2_spouse_nric_num': self.instance.get_sponsor_2_spouse_nric_full()})
        self.initial.update({'sponsor_2_spouse_fin_num': self.instance.get_sponsor_2_spouse_fin_full()})
        self.initial.update({'sponsor_2_spouse_passport_num': self.instance.get_sponsor_2_spouse_passport_full()})
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Sponsors
            Row(
                Column(
                    HTML(
                        """
                        <h5 class="my-3">Sponsors</h5>
                    """),


                    Row(
                        Column(
                            HTML(
                                """
                                <h5 class="my-3">Sponsor 1's Information</h5>
                            """),
                            Row(
                                Column(
                                    'sponsor_1_relationship',
                                    css_class='form-group col-md-6',
                                ),
                                Column(
                                    'sponsor_1_worked_in_sg',
                                    css_class='form-group col-md-6',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'sponsor_1_name',
                                    css_class='form-group col-md-6',
                                ),
                                Column(
                                    'sponsor_1_gender',
                                    css_class='form-group col-md-6',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    Field(
                                        'sponsor_1_date_of_birth',
                                        type='text',
                                        onfocus="(this.type='date')",
                                        placeholder='Sponsor 1 date of birth'
                                    ),
                                    css_class='form-group col-md-6',
                                ),
                                Column(
                                    'sponsor_1_nric_num',
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
                                    HTML(
                                        """
                                        <h5 class="my-3">Sponsor 1 Spouse's Information</h5>
                                    """),
                                    Row(
                                        Column(
                                            'sponsor_1_marriage_sg_registered',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        Column(
                                            'sponsor_1_spouse_name',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        css_class='form-row',
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_1_spouse_gender',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        Column(
                                            Field(
                                                'sponsor_1_spouse_date_of_birth',
                                                type='text',
                                                onfocus="(this.type='date')",
                                                placeholder='Sponsor 1 spouse date of birth'
                                            ),
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        css_class='form-row',
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_1_spouse_nationality',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        Column(
                                            'sponsor_1_spouse_residential_status',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        css_class='form-row',
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_1_spouse_nric_num',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        Column(
                                            'sponsor_1_spouse_fin_num',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        css_class='form-row',
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_1_spouse_passport_num',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        Column(
                                            Field(
                                                'sponsor_1_spouse_passport_date',
                                                type='text',
                                                onfocus="(this.type='date')",
                                                placeholder='Sponsor 1 spouse passport expiry date',
                                            ),
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        css_class='form-row',
                                    ),
                                ),
                                id="sponsor_1_spouse",
                                # hidden='true',
                            ),
                        ),
                        id="sponsor_1",
                    ),

                    # Is Sponsor 2 required?
                    Row(
                        Column(
                            HTML(
                                """
                                <h5 class="my-3">Is Sponsor 2 required?</h5>
                            """),
                            Row(
                                Column(
                                    'sponsor_2_required',
                                    css_class='form-group col-md-6',
                                ),
                                css_class='form-row',
                            ),
                        ),
                    ),

                    # Sponsor 2
                    Row(
                        Column(
                            HTML(
                                """
                                <h5 class="my-3">Sponsor 2's Information</h5>
                            """),
                            Row(
                                Column(
                                    'sponsor_2_relationship',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_worked_in_sg',
                                    css_class='form-group col-md-6',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'sponsor_2_name',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_gender',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    Field(
                                        'sponsor_2_date_of_birth',
                                        type='text',
                                        onfocus="(this.type='date')",
                                        placeholder='Sponsor 2 date of birth',
                                    ),
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_nric_num',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'sponsor_2_nationality',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_residential_status',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'sponsor_2_mobile_number',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_email',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'sponsor_2_address_1',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_address_2',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'sponsor_2_post_code',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_marital_status',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                css_class='form-row',
                            ),
                            # Sponsor 2 spouse
                            Row(
                                Column(
                                    HTML(
                                        """
                                        <h5 class="my-3">Sponsor 2 Spouse's Information</h5>
                                    """),
                                    Row(
                                        Column(
                                            'sponsor_2_marriage_sg_registered',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        Column(
                                            'sponsor_2_spouse_name',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        css_class='form-row',
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_2_spouse_gender',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        Column(
                                            Field(
                                                'sponsor_2_spouse_date_of_birth',
                                                type='text',
                                                onfocus="(this.type='date')",
                                                placeholder='Sponsor 2 date of birth',
                                            ),
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        css_class='form-row',
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_2_spouse_nationality',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        Column(
                                            'sponsor_2_spouse_residential_status',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        css_class='form-row',
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_2_spouse_nric_num',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        Column(
                                            'sponsor_2_spouse_fin_num',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        css_class='form-row'
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_2_spouse_passport_num',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        Column(
                                            Field(
                                                'sponsor_2_spouse_passport_date',
                                                type='text',
                                                onfocus="(this.type='date')",
                                                placeholder='Sponsor 2 spouse passport expiry date',
                                            ),
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        css_class='form-row',
                                    ),
                                ),
                                id="sponsor_2_spouse",
                                # hidden="true",
                            ),
                        ),
                        id="sponsor_2",
                        # hidden="true",
                    ),

                    # Income Details
                    # HTML(
                    #     """
                    #     <h5 class="my-3">Income Details</h5>
                    # """),
                    # Row(
                    #     Column(
                    #         PrependedText(
                    #             'monthly_income', '$',
                    #             min='0', max='9999999',
                    #         ),
                    #         css_class='form-group col-md-6',
                    #         id='sponsor_monthly_income',
                    #     ),
                    #     css_class='form-row',
                    # ),
                    # id='sponsors',
                ),
                id='sponsors-section',
            ),

            # Submit
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )
    
    def clean_sponsor_1_nric_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_1_nric_nonce, self.instance.sponsor_1_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_sponsor_1_spouse_nric_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_spouse_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_1_spouse_nric_nonce, self.instance.sponsor_1_spouse_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_sponsor_1_spouse_fin_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_spouse_fin_num')
        error_msg = helper_functions.validate_fin(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_1_spouse_fin_nonce, self.instance.sponsor_1_spouse_fin_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_sponsor_1_spouse_passport_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_1_spouse_passport_num')
        error_msg = helper_functions.validate_passport(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_1_spouse_passport_nonce, self.instance.sponsor_1_spouse_passport_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_sponsor_2_nric_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_2_nric_nonce, self.instance.sponsor_2_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_sponsor_2_spouse_nric_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_spouse_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_2_spouse_nric_nonce, self.instance.sponsor_2_spouse_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_sponsor_2_spouse_fin_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_spouse_fin_num')
        error_msg = helper_functions.validate_fin(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_2_spouse_fin_nonce, self.instance.sponsor_2_spouse_fin_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_sponsor_2_spouse_passport_num(self):
        cleaned_field = self.cleaned_data.get('sponsor_2_spouse_passport_num')
        error_msg = helper_functions.validate_passport(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.sponsor_2_spouse_passport_nonce, self.instance.sponsor_2_spouse_passport_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

class EmployerJointApplicantForm(forms.ModelForm):
    class Meta:
        model = models.EmployerJointApplicant
        exclude = [
            'employer',
            'joint_applicant_nric_nonce',
            'joint_applicant_nric_tag',
            'joint_applicant_spouse_nric_nonce',
            'joint_applicant_spouse_nric_tag',
            'joint_applicant_spouse_fin_nonce',
            'joint_applicant_spouse_fin_tag',
            'joint_applicant_spouse_passport_nonce',
            'joint_applicant_spouse_passport_tag',
        ]

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.initial.update({'joint_applicant_nric_num': self.instance.get_joint_applicant_nric_full()})
        self.initial.update({'joint_applicant_spouse_nric_num': self.instance.get_joint_applicant_spouse_nric_full()})
        self.initial.update({'joint_applicant_spouse_fin_num': self.instance.get_joint_applicant_spouse_fin_full()})
        self.initial.update({'joint_applicant_spouse_passport_num': self.instance.get_joint_applicant_spouse_passport_full()})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Joint Applicants
            Row(
                Column(
                    HTML(
                        """
                        <h5 class="my-3">Joint Applicant's Information</h5>
                    """),
                    Row(
                        Column(
                            'joint_applicant_relationship',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'joint_applicant_worked_in_sg',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            'joint_applicant_name',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'joint_applicant_gender',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row',
                    ),
                    Row(
                        Column(
                            Field(
                                'joint_applicant_date_of_birth',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Joint applicant date of birth'
                            ),
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'joint_applicant_nric_num',
                            css_class='form-group col-md-6',
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
                            HTML(
                                """
                                <h5 class="my-3">Joint Applicant Spouse's Information</h5>
                            """),
                            Row(
                                Column(
                                    'joint_applicant_marriage_sg_registered',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                Column(
                                    'joint_applicant_spouse_name',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'joint_applicant_spouse_gender',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                Column(
                                    Field(
                                        'joint_applicant_spouse_date_of_birth',
                                        type='text',
                                        onfocus="(this.type='date')",
                                        placeholder='Joint applicant spouse date of birth'
                                    ),
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'joint_applicant_spouse_nric_num',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                Column(
                                    'joint_applicant_spouse_fin_num',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'joint_applicant_spouse_passport_num',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                Column(
                                    Field(
                                        'joint_applicant_spouse_passport_date',
                                        type='text',
                                        onfocus="(this.type='date')",
                                        placeholder='Joint applicant spouse passport expiry date',
                                    ),
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                css_class='form-row',
                            ),
                            Row(
                                Column(
                                    'joint_applicant_spouse_nationality',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                Column(
                                    'joint_applicant_spouse_residential_status',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                css_class='form-row',
                            ),
                        ),
                        id="joint_applicant_spouse",
                        # hidden="true",
                    ),
                ),
            ),

            # HTML(
            #     """
            #     <h5 class="my-3">Income Details</h5>
            # """),
            # Row(
            #     Column(
            #         PrependedText(
            #             'monthly_income', '$',
            #             min='0', max='9999999',
            #         ),
            #         css_class='form-group col-md-6',
            #     ),
            #     css_class='form-row',
            # ),
            
            # Submit
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )
    
    def clean_joint_applicant_nric_num(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.joint_applicant_nric_nonce, self.instance.joint_applicant_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_joint_applicant_spouse_nric_num(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_spouse_nric_num')
        error_msg = helper_functions.validate_nric(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.joint_applicant_spouse_nric_nonce, self.instance.joint_applicant_spouse_nric_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_joint_applicant_spouse_fin_num(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_spouse_fin_num')
        error_msg = helper_functions.validate_fin(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.joint_applicant_spouse_fin_nonce, self.instance.joint_applicant_spouse_fin_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_joint_applicant_spouse_passport_num(self):
        cleaned_field = self.cleaned_data.get('joint_applicant_spouse_passport_num')
        error_msg = helper_functions.validate_passport(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.joint_applicant_spouse_passport_nonce, self.instance.joint_applicant_spouse_passport_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

class EmployerIncomeDetailsForm(forms.ModelForm):
    class Meta:
        model = models.EmployerIncome
        exclude = [
            'employer'
        ]

    def __init__(self, *args, **kwargs):
        # self.user_pk = kwargs.pop('user_pk')
        # self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Income Details
            Row(
                Column(
                    HTML(
                        """
                        <h5 class="my-3">Income Details</h5>
                    """),
                    Row(
                        Column(
                            'worked_in_sg',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'monthly_income',
                            css_class='form-group col-md-6',
                        ),
                        css_class='form-row'
                    ),
                ),
                id='income-details-section',
            ),

            # Submit
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

class EmployerDocForm(forms.ModelForm):
    class Meta:
        model = models.EmployerDoc
        exclude = []

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        if self.agency_user_group==om_constants.AG_OWNERS:
            self.fields['fdw'].queryset = (
                Maid.objects.filter(agency=get_user_model().objects.get(
                    pk=self.user_pk).agency_owner.agency)
            )
        else:
            self.fields['fdw'].queryset = (
                Maid.objects.filter(agency=get_user_model().objects.get(
                    pk=self.user_pk).agency_employee.agency)
            )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(
                """
                <h5 class="doc-section-header">Case Information</h5>
            """),
            
            Row(
                Column(
                    'case_ref_no',
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field(
                        'agreement_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Contract date'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'employer',
                    css_class='form-group col-md-6',
                ),
                Column(
                    'fdw',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'fdw_salary',
                    css_class='form-group col-md-6',
                ),
                Column(
                    'fdw_loan',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'fdw_off_days',
                    css_class='form-group col-md-6',
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

class DocServiceFeeScheduleForm(forms.ModelForm):
    class Meta:
        model = models.DocServiceFeeSchedule
        exclude = [
            'employer_doc',
            'fdw_replaced_passport_nonce',
            'fdw_replaced_passport_tag',
        ]

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.initial.update({'fdw_replaced_passport_num': self.instance.get_fdw_replaced_passport_full()})

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(
                """
                <h5 class="doc-section-header" id="id-doc-service-fee-schedule">Service Fee Schedule</h5>
            """),

            Row(
                Column(
                    'is_new_case',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),

            # Form B
            Row(
                Column(
                    'fdw_replaced_name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'fdw_replaced_passport_num',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row',
                id="form_b",
            ),
            Row(
                Column(
                    PrependedText(
                        'b4_loan_transferred', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row',
                id="form_b",
            ),

            # Form A
            HTML(
                """
                <h6>Service Fee</h6>
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

            HTML(
                """
                <h6>Administrative Cost</h6>
            """),
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
                    PrependedText(
                        'b2h_food_lodging', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2i1_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2i1_other_services_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2i2_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2i2_other_services_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'b2i3_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2i3_other_services_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'b2j_replacement_months',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            PrependedText(
                                'b2j_replacement_cost', '$',
                                min='0', max='1000',
                            ),
                            css_class='form-group col-md-6'
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            PrependedText(
                                'b2k_work_permit_renewal', '$',
                                min='0', max='1000',
                            ),
                            css_class='form-group col-md-6'
                        ),
                        css_class='form-row'
                    ),
                ),
                css_class='form-row',
                id="b2j_b2k"
            ),

            HTML(
                """
                <h6>Placement Fee</h6>
            """),
            Row(
                Column(
                    PrependedText(
                        'b3_agency_fee', '$',
                        min='0', max='10000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),

            HTML(
                """
                <h6>Deposit</h6>
            """),
            Row(
                Column(
                    PrependedText(
                        'ca_deposit_amount', '$',
                        min='0', max='10000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    Field(
                        'ca_deposit_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Deposit paid date'
                    ),
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

    def clean_fdw_replaced_passport_num(self):
        cleaned_field = self.cleaned_data.get('fdw_replaced_passport_num')
        error_msg = helper_functions.validate_passport(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.fdw_replaced_passport_nonce, self.instance.fdw_replaced_passport_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

    def clean_b4_loan_transferred(self):
        is_new_case = self.cleaned_data.get('is_new_case')
        cleaned_field = self.cleaned_data.get('b4_loan_transferred')

        if is_new_case:
            return cleaned_field
        elif not is_new_case and not cleaned_field:
            raise ValidationError('Loan being transferred is a required \
                field')
        else:
            return cleaned_field

class DocServAgmtEmpCtrForm(forms.ModelForm):
    class Meta:
        model = models.DocServAgmtEmpCtr
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
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
                css_class='form-row'
            ),

            Row(
                Column(
                    'c4_1_number_of_replacements',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c4_1_replacement_period',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c4_1_replacement_after_min_working_days',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c4_1_5_replacement_deadline',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            
            Row(
                Column(
                    'c5_1_1_deployment_deadline',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'c5_1_1_failed_deployment_refund', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'c5_1_2_refund_within_days',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'c5_1_2_before_fdw_arrives_charge', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'c5_1_2_after_fdw_arrives_charge', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c5_2_2_can_transfer_refund_within',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
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

# class DocEmploymentContractForm(forms.ModelForm):
#     class Meta:
#         model = models.DocEmploymentContract
#         exclude = ['employer_doc']

#     def __init__(self, *args, **kwargs):
#         self.user_pk = kwargs.pop('user_pk')
#         self.agency_user_group = kwargs.pop('agency_user_group')
#         super().__init__(*args, **kwargs)

#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             HTML(
#                 """
#                 <h5 class="doc-section-header" id="id-doc-employment-contract">Employment Contract</h5>
#             """),
#             Row(
#                 Column(
#                     'c3_5_fdw_sleeping_arrangement',
#                     css_class='form-group col-md-6'
#                 ),
#                 Column(
#                     'c4_1_termination_notice',
#                     css_class='form-group col-md-6'
#                 ),
#                 css_class='form-row'
#             ),
            
#             # Submit
#             Row(
#                 Column(
#                     Submit(
#                         'submit',
#                         'Submit',
#                         css_class="btn btn-primary w-50"
#                     ),
#                     css_class='form-group col-12 text-center'
#                 ),
#                 css_class='form-row'
#             )
#         )

class DocSafetyAgreementForm(forms.ModelForm):
    class Meta:
        model = models.DocSafetyAgreement
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
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

    def clean(self):
        window_exterior_location_verbose_name = models.EmployerDoc._meta.get_field('window_exterior_location').verbose_name
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
        
        grilles_installed_verbose_name = models.EmployerDoc._meta.get_field('grilles_installed_require_cleaning').verbose_name
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
        
        adult_supervision_verbose_name = models.EmployerDoc._meta.get_field('adult_supervision').verbose_name
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
        
        verifiy_employer_understands_verbose_name = models.EmployerDoc._meta.get_field('verifiy_employer_understands_window_cleaning').verbose_name
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
        model = models.EmployerDocSig
        fields = ['employer_slug']
        labels = {
            'employer_slug': _('Employer signature URL'),
        }

    def __init__(self, *args, **kwargs):
        self.model_field_name = kwargs.pop('model_field_name')
        self.form_fields = kwargs.pop('form_fields')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
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

class EmployerDocMaidStatusForm(forms.ModelForm):
    class Meta:
        model = models.EmployerDocMaidStatus
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.agency_user_group = kwargs.pop('agency_user_group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('''
                <h3>FDW Status</h3>
                '''
            ),
            Row(
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
                        'shn_end_date',
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
                        'fdw_work_commencement_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='FDW work commencement date'
                    ),
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

# class EmployerPaymentTransactionForm(forms.ModelForm):
#     class Meta:
#         model = models.EmployerPaymentTransaction
#         exclude = ['employer_doc']

#     def __init__(self, *args, **kwargs):
#         self.user_pk = kwargs.pop('user_pk')
#         self.agency_user_group = kwargs.pop('agency_user_group')
#         super().__init__(*args, **kwargs)

#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Row(
#                 Column(
#                     Field(
#                         'transaction_date',
#                         type='text',
#                         onfocus="(this.type='date')",
#                         placeholder='Transaction date'
#                     ),
#                     css_class='form-group col-md-4'
#                 ),
#                 Column(
#                     PrependedText(
#                         'amount', '$',
#                         min='0', max='10000',
#                     ),
#                     css_class='form-group col-md-4'
#                 ),
#                 Column(
#                     'transaction_type',
#                     css_class='form-group col-md-4'
#                 ),
#                 css_class='form-row'
#             ),
#             Submit('submit', 'Submit')
#         )

# class JobOrderForm(forms.ModelForm):
#     class Meta:
#         model = models.JobOrder
#         widgets = {'job_order_pdf': forms.FileInput(attrs={'accept': 'application/pdf'})}
#         exclude = ['employer_doc']

#     def __init__(self, *args, **kwargs):
#         self.user_pk = kwargs.pop('user_pk')
#         self.agency_user_group = kwargs.pop('agency_user_group')
#         super().__init__(*args, **kwargs)

#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Field(
#                 'job_order_pdf',
#             ),
#             Submit('submit', 'Submit')
#         )

# Signature Forms
class SignatureForm(forms.ModelForm):
    class Meta:
        model = models.EmployerDocSig
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
        model = models.EmployerDocSig
        exclude = '__all__'
        fields = ['employer_token']
    
    # Employer fields
    nric = forms.CharField()
    mobile = forms.IntegerField()
    
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
        super().__init__(*args, **kwargs)

        self.fields['nric'].label = 'NRIC'
        self.helper = FormHelper()
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
            else:
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
                False
            # self.is_fdw
            #     and ( ############################################## TO BE UPDATED
            #         self.cleaned_data.get('validation_1', '') ==
            #         '1'
            #         and
            #         int(self.cleaned_data.get('validation_2', 0)) ==
            #         int(1)
            #     ) ############################################## TO BE UPDATED
            )
        ):
            verification_token = secrets.token_urlsafe(128)
            self.cleaned_data[self.token_field_name] = verification_token
            self.session['signature_token'] = verification_token
            self.session.set_expiry(60*30) # Session expires in 30 mins
            return self.cleaned_data
        else:
            raise ValidationError(
                'The details you entered did not match our records')
