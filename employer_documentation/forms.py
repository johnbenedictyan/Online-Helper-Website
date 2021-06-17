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
from crispy_forms.layout import Layout, Field, Fieldset, Submit, Row, Column, HTML, Hidden, Button
from crispy_forms.bootstrap import FormActions, PrependedText, StrictButton, UneditableField

# Imports from local apps
from . import models, constants
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
        self.authority = kwargs.pop('authority')
        super().__init__(*args, **kwargs)

        # Decryption
        self.initial.update({'employer_nric_num': self.instance.get_employer_nric_full()})
        self.initial.update({'employer_fin_num': self.instance.get_employer_fin_full()})
        self.initial.update({'employer_passport_num': self.instance.get_employer_passport_full()})
        self.initial.update({'spouse_nric_num': self.instance.get_employer_spouse_nric_full()})
        self.initial.update({'spouse_fin_num': self.instance.get_employer_spouse_fin_full()})
        self.initial.update({'spouse_passport_num': self.instance.get_employer_spouse_passport_full()})
        
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
                )
            ),
            Row(
                Column(
                    # Note: Current position in layout helper object is self.helper.layout.fields[1][1].
                    # If position is changed, MUST update 'del self.helper.layout.fields[1][1]' line
                    # as this removes this object from the layout helper.
                    'agency_employee',
                    css_class='form-group col-md-6'
                )
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
                )
            ),
            Row(
                Column(
                    PrependedText(
                        'employer_mobile_number', '+65',
                    ),
                    css_class='form-group col-md-6',
                ),
                Column(
                    PrependedText(
                        'employer_home_number', '+65',
                    ),
                    css_class='form-group col-md-6',
                )
            ),
            Row(
                Column(
                    'employer_email',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_address_1',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'employer_address_2',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_post_code',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    Field(
                        'employer_date_of_birth',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Employer date of birth',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_nationality',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'employer_residential_status',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'employer_nric_num',
                    css_class='form-group col-md-6',
                    id='employer_id_nric',
                )
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
                id='employer_id_other'
            ),
            Row(
                Column(
                    Field(
                        'employer_passport_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Employer passport expiry date',
                    ),
                    css_class='form-group col-md-6',
                    id='employer_id_other_2',
                ),
                Column(
                    'employer_marital_status',
                    css_class='form-group col-md-6'
                )
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
                        ),
                        Column(
                            'spouse_gender',
                            css_class='form-group col-md-6 employer-spouse spouse-only',
                        )
                    ),
                    Row(
                        Column(
                            Field(
                                'spouse_date_of_birth',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Employer spouse date of birth',
                            ),
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'spouse_nationality',
                            css_class='form-group col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            'spouse_residential_status',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'spouse_nric_num',
                            css_class='form-group col-md-6',
                            id='spouse_id_nric',
                        )
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
                        id='spouse_id_other',
                    ),
                    Row(
                        Column(
                            Field(
                                'spouse_passport_date',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Employer spouse passport expiry date',
                            ),
                            css_class='form-group col-md-6',
                            id='spouse_id_other_2',
                        ),
                        Column(
                            'employer_marriage_sg_registered',
                            css_class='form-group col-md-6'
                        )
                    ),
                ),
                id='spouse-section',
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
                )
            )
        )

        if self.authority==om_constants.AG_OWNERS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_owner.agency
                )
            )
        elif self.authority==om_constants.AG_ADMINS:
            self.fields['agency_employee'].queryset = (
                AgencyEmployee.objects.filter(
                    agency=self.user_obj.agency_employee.agency
                )
            )
        elif self.authority==om_constants.AG_MANAGERS:
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
                if self.authority==om_constants.AG_OWNERS:
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
        employer_residential_status = self.cleaned_data.get('employer_residential_status')
        if employer_residential_status==constants.ResidentialStatusFullChoices.SC or employer_residential_status==constants.ResidentialStatusFullChoices.PR:
            empty_field = _("NRIC field cannot be empty")
            error_msg = empty_field if not cleaned_field else helper_functions.validate_nric(cleaned_field)
            if error_msg:
                raise ValidationError(error_msg)
            else:
                ciphertext, self.instance.employer_nric_nonce, self.instance.employer_nric_tag = helper_functions.encrypt_string(
                    cleaned_field,
                    settings.ENCRYPTION_KEY
                )
                return ciphertext
        else:
            return None

    def clean_employer_fin_num(self):
        cleaned_field = self.cleaned_data.get('employer_fin_num')
        employer_residential_status = self.cleaned_data.get('employer_residential_status')
        if not employer_residential_status==constants.ResidentialStatusFullChoices.SC and not employer_residential_status==constants.ResidentialStatusFullChoices.PR:
            empty_field = _("FIN field cannot be empty")
            error_msg = empty_field if not cleaned_field else helper_functions.validate_fin(cleaned_field)
            if error_msg:
                raise ValidationError(error_msg)
            else:
                ciphertext, self.instance.employer_fin_nonce, self.instance.employer_fin_tag = helper_functions.encrypt_string(
                    cleaned_field,
                    settings.ENCRYPTION_KEY
                )
                return ciphertext
        else:
            return None

    def clean_employer_passport_num(self):
        cleaned_field = self.cleaned_data.get('employer_passport_num')
        employer_residential_status = self.cleaned_data.get('employer_residential_status')
        if not employer_residential_status==constants.ResidentialStatusFullChoices.SC and not employer_residential_status==constants.ResidentialStatusFullChoices.PR:
            empty_field = _("Passport field cannot be empty")
            error_msg = empty_field if not cleaned_field else helper_functions.validate_passport(cleaned_field)
            if error_msg:
                raise ValidationError(error_msg)
            else:
                ciphertext, self.instance.employer_passport_nonce, self.instance.employer_passport_tag = helper_functions.encrypt_string(
                    cleaned_field,
                    settings.ENCRYPTION_KEY
                )
                return ciphertext
        else:
            return None

    def clean_employer_passport_date(self):
        cleaned_field = self.cleaned_data.get('employer_passport_date')
        employer_residential_status = self.cleaned_data.get('employer_residential_status')
        if not employer_residential_status==constants.ResidentialStatusFullChoices.SC and not employer_residential_status==constants.ResidentialStatusFullChoices.PR:
            empty_field = _("Passport expiry date field cannot be empty")
            error_msg = empty_field if not cleaned_field else None
            if error_msg:
                raise ValidationError(error_msg)
            else:
                return cleaned_field
        else:
            return None

    def clean_spouse_nric_num(self):
        cleaned_field = self.cleaned_data.get('spouse_nric_num')
        marital_status = self.cleaned_data.get('employer_marital_status')
        if marital_status==constants.MaritalStatusChoices.MARRIED:
            spouse_residential_status = self.cleaned_data.get('spouse_residential_status')
            if spouse_residential_status==constants.ResidentialStatusFullChoices.SC or spouse_residential_status==constants.ResidentialStatusFullChoices.PR:
                empty_field = _("NRIC field cannot be empty")
                error_msg = empty_field if not cleaned_field else helper_functions.validate_nric(cleaned_field)
                if error_msg:
                    raise ValidationError(error_msg)
                else:
                    ciphertext, self.instance.spouse_nric_nonce, self.instance.spouse_nric_tag = helper_functions.encrypt_string(
                        cleaned_field,
                        settings.ENCRYPTION_KEY
                    )
                    return ciphertext
            else:
                return None
        else:
            return None

    def clean_spouse_fin_num(self):
        cleaned_field = self.cleaned_data.get('spouse_fin_num')
        marital_status = self.cleaned_data.get('employer_marital_status')
        if marital_status==constants.MaritalStatusChoices.MARRIED:
            spouse_residential_status = self.cleaned_data.get('spouse_residential_status')
            if not spouse_residential_status==constants.ResidentialStatusFullChoices.SC and not spouse_residential_status==constants.ResidentialStatusFullChoices.PR:
                empty_field = _("FIN field cannot be empty")
                error_msg = empty_field if not cleaned_field else None
                if error_msg:
                    raise ValidationError(error_msg)
                else:
                    ciphertext, self.instance.spouse_fin_nonce, self.instance.spouse_fin_tag = helper_functions.encrypt_string(
                        cleaned_field,
                        settings.ENCRYPTION_KEY
                    )
                    return ciphertext
            else:
                return None
        else:
            return None

    def clean_spouse_passport_num(self):
        cleaned_field = self.cleaned_data.get('spouse_passport_num')
        marital_status = self.cleaned_data.get('employer_marital_status')
        if marital_status==constants.MaritalStatusChoices.MARRIED:
            spouse_residential_status = self.cleaned_data.get('spouse_residential_status')
            if not spouse_residential_status==constants.ResidentialStatusFullChoices.SC and not spouse_residential_status==constants.ResidentialStatusFullChoices.PR:
                empty_field = _("Passport field cannot be empty")
                error_msg = empty_field if not cleaned_field else None
                if error_msg:
                    raise ValidationError(error_msg)
                else:
                    ciphertext, self.instance.spouse_passport_nonce, self.instance.spouse_passport_tag = helper_functions.encrypt_string(
                        cleaned_field,
                        settings.ENCRYPTION_KEY
                    )
                    return ciphertext
            else:
                return None
        else:
            return None

    def clean_spouse_passport_date(self):
        cleaned_field = self.cleaned_data.get('employer_passport_date')
        marital_status = self.cleaned_data.get('employer_marital_status')
        if marital_status==constants.MaritalStatusChoices.MARRIED:
            spouse_residential_status = self.cleaned_data.get('spouse_residential_status')
            if not spouse_residential_status==constants.ResidentialStatusFullChoices.SC and not spouse_residential_status==constants.ResidentialStatusFullChoices.PR:
                empty_field = _("Passport expiry date field cannot be empty")
                error_msg = empty_field if not cleaned_field else None
                if error_msg:
                    raise ValidationError(error_msg)
                else:
                    return cleaned_field
            else:
                return None
        else:
            return None

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
        self.authority = kwargs.pop('authority')
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
                                    'sponsor_1_name',
                                    css_class='form-group col-md-6',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_1_gender',
                                    css_class='form-group col-md-6',
                                ),
                                Column(
                                    'sponsor_1_nric_num',
                                    css_class='form-group col-md-6',
                                )
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
                                    'sponsor_1_nationality',
                                    css_class='form-group col-md-6',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_1_residential_status',
                                    css_class='form-group col-md-6',
                                ),
                                Column(
                                    PrependedText(
                                        'sponsor_1_mobile_number', '+65',
                                    ),
                                    css_class='form-group col-md-6',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_1_email',
                                    css_class='form-group col-md-6',
                                ),
                                Column(
                                    'sponsor_1_address_1',
                                    css_class='form-group col-md-6',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_1_address_2',
                                    css_class='form-group col-md-6',
                                ),
                                Column(
                                    'sponsor_1_post_code',
                                    css_class='form-group col-md-6',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_1_marital_status',
                                    css_class='form-group col-md-6',
                                )
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
                                        )
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
                                        )
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_1_spouse_nationality',
                                            css_class='form-group col-md-6 spouse-1',
                                        ),
                                        Column(
                                            'sponsor_1_spouse_residential_status',
                                            css_class='form-group col-md-6 spouse-1',
                                        )
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_1_spouse_nric_num',
                                            css_class='form-group col-md-6 spouse-1',
                                            id='sponsor1spouse_id_nric',
                                        ),
                                        Column(
                                            'sponsor_1_spouse_fin_num',
                                            css_class='form-group col-md-6 spouse-1',
                                            id='sponsor1spouse_id_fin',
                                        )
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
                                        id='sponsor1spouse_id_passport',
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
                                )
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
                                    'sponsor_2_name',
                                    css_class='form-group col-md-6 sponsor-2',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_2_gender',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_nric_num',
                                    css_class='form-group col-md-6 sponsor-2',
                                )
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
                                    'sponsor_2_nationality',
                                    css_class='form-group col-md-6 sponsor-2',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_2_residential_status',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    PrependedText(
                                        'sponsor_2_mobile_number', '+65',
                                    ),
                                    css_class='form-group col-md-6',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_2_email',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_address_1',
                                    css_class='form-group col-md-6 sponsor-2',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_2_address_2',
                                    css_class='form-group col-md-6 sponsor-2',
                                ),
                                Column(
                                    'sponsor_2_post_code',
                                    css_class='form-group col-md-6 sponsor-2',
                                )
                            ),
                            Row(
                                Column(
                                    'sponsor_2_marital_status',
                                    css_class='form-group col-md-6 sponsor-2',
                                )
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
                                        )
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
                                        )
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_2_spouse_nationality',
                                            css_class='form-group col-md-6 spouse-2',
                                        ),
                                        Column(
                                            'sponsor_2_spouse_residential_status',
                                            css_class='form-group col-md-6 spouse-2',
                                        )
                                    ),
                                    Row(
                                        Column(
                                            'sponsor_2_spouse_nric_num',
                                            css_class='form-group col-md-6 spouse-2',
                                            id='sponsor2spouse_id_nric',
                                        ),
                                        Column(
                                            'sponsor_2_spouse_fin_num',
                                            css_class='form-group col-md-6 spouse-2',
                                            id='sponsor2spouse_id_fin',
                                        )
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
                                        id='sponsor2spouse_id_passport',
                                    ),
                                ),
                                id="sponsor_2_spouse",
                                # hidden="true",
                            ),
                        ),
                        id="sponsor_2",
                        # hidden="true",
                    ),
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
                    css_class='form-group col-md-6 text-center'
                )
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
        self.authority = kwargs.pop('authority')
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
                            'joint_applicant_name',
                            css_class='form-group col-md-6',
                        )
                    ),
                    Row(
                        Column(
                            'joint_applicant_gender',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            Field(
                                'joint_applicant_date_of_birth',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Joint applicant date of birth'
                            ),
                            css_class='form-group col-md-6',
                        )
                    ),
                    Row(
                        Column(
                            'joint_applicant_nric_num',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'joint_applicant_nationality',
                            css_class='form-group col-md-6',
                        )
                    ),
                    Row(
                        Column(
                            'joint_applicant_residential_status',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'joint_applicant_address_1',
                            css_class='form-group col-md-6',
                        )
                    ),
                    Row(
                        Column(
                            'joint_applicant_address_2',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'joint_applicant_post_code',
                            css_class='form-group col-md-6',
                        )
                    ),
                    Row(
                        Column(
                            'joint_applicant_marital_status',
                            css_class='form-group col-md-6',
                        )
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
                                )
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
                                )
                            ),
                            Row(
                                Column(
                                    'joint_applicant_spouse_nationality',
                                    css_class='form-group col-md-6 spouse-1',
                                ),
                                Column(
                                    'joint_applicant_spouse_residential_status',
                                    css_class='form-group col-md-6 spouse-1',
                                )
                            ),
                            Row(
                                Column(
                                    'joint_applicant_spouse_nric_num',
                                    css_class='form-group col-md-6 spouse-1',
                                    id='ja_spouse_id_nric',
                                ),
                                Column(
                                    'joint_applicant_spouse_fin_num',
                                    css_class='form-group col-md-6 spouse-1',
                                    id='ja_spouse_id_fin',
                                )
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
                                id='ja_spouse_id_passport',
                            ),
                        ),
                        id="joint_applicant_spouse",
                        # hidden="true",
                    ),
                ),
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
                )
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
        self.user_pk = kwargs.pop('user_pk')
        self.authority = kwargs.pop('authority')
        self.monthly_income_label = kwargs.pop('monthly_income_label')
        super().__init__(*args, **kwargs)

        # Set form field label based on applicant type
        self.fields['monthly_income'].label = self.monthly_income_label[0]
        self.fields['worked_in_sg'].label = self.monthly_income_label[1]

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
                        )
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
                )
            )
        )

class EmployerHouseholdDetailsForm(forms.ModelForm):
    class Meta:
        model = models.EmployerHousehold
        exclude = [
            'employer',
            'household_id_nonce',
            'household_id_tag',
        ]

    def save(self, *args, **kwargs):
        self.instance.employer = self.employer
        return super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.employer_id = kwargs.pop('employer_id')
        self.employer = models.Employer.objects.get(
            pk=self.employer_id
        )
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Household Details
            Row(
                Column(
                    HTML(
                        """
                        <h5 class="my-3">Household Details</h5>
                    """),
                    Row(
                        Column(
                            'household_name',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'household_id_type',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'household_id_num',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'household_date_of_birth',
                            css_class='form-group col-md-6',
                        ),
                        Column(
                            'household_relationship',
                            css_class='form-group col-md-6'
                        )
                    ),
                ),
                id='household-section',
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
                )
            )
        )

    def clean_household_id_num(self):
        cleaned_field = self.cleaned_data.get('household_id_num')
        error_msg = helper_functions.validate_passport(cleaned_field)
        if error_msg:
            raise ValidationError(error_msg)
        else:
            ciphertext, self.instance.household_id_nonce, self.instance.household_id_tag = helper_functions.encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY
            )
            return ciphertext

class MaidInventoryForm(forms.ModelForm):
    class Meta:
        model = models.MaidInventory
        exclude = [
            'employer_doc',
        ]
    
    def save(self, *args, **kwargs):
        self.instance.employer_doc = self.employer_doc
        return super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.employer_doc_id = kwargs.pop('employer_doc_id')
        self.employer_doc = models.EmployerDoc.objects.get(
            pk=self.employer_doc_id
        )
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            Field(
                                'DELETE'
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            'item_name',
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class='form-group'
            )
        )

class EmployerDocForm(forms.ModelForm):
    class Meta:
        model = models.EmployerDoc
        exclude = []

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.authority = kwargs.pop('authority')
        self.agency_id = kwargs.pop('agency_id')
        super().__init__(*args, **kwargs)

        self.fields['employer'].queryset = (
            models.Employer.objects.filter(
                agency_employee__agency__pk=self.agency_id,
            )
        )

        if self.authority==om_constants.AG_OWNERS:
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
                )
            ),
            Row(
                Column(
                    'employer',
                    css_class='form-group col-md-6',
                ),
                Column(
                    'fdw',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    PrependedText(
                        'fdw_salary', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'fdw_loan', '$',
                        min='0', max='10000',
                    ),
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'fdw_off_days',
                    css_class='form-group col-md-6',
                ),
                Column(
                    PrependedText(
                        'fdw_monthly_loan_repayment', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'fdw_off_day_of_week',
                    css_class='form-group col-md-6',
                )
            ),
            # Submit
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                )
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
        self.authority = kwargs.pop('authority')
        self.level_1_pk = kwargs.pop('level_1_pk')
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
                )
            ),

            # Form B
            Row(
                Column(
                    Row(
                        Column(
                            'fdw_replaced_name',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'fdw_replaced_passport_num',
                            css_class='form-group col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            PrependedText(
                                'b4_loan_transferred', '$',
                                min='0', max='1000',
                            ),
                            css_class='form-group col-md-6'
                        )
                    ),
                ),
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
                )
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
                )
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
                )
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
                        'b2f_sip', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'b2g1_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2g1_other_services_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'b2g2_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2g2_other_services_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'b2g3_other_services_description',
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'b2g3_other_services_fee', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'b2h_replacement_months',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            PrependedText(
                                'b2h_replacement_cost', '$',
                                min='0', max='1000',
                            ),
                            css_class='form-group col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            PrependedText(
                                'b2i_work_permit_renewal', '$',
                                min='0', max='1000',
                            ),
                            css_class='form-group col-md-6'
                        )
                    ),
                ),
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
                )
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
                )
            ),

            # Submit
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'case_update_route' level_1_pk %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                )
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
        self.authority = kwargs.pop('authority')
        self.level_1_pk = kwargs.pop('level_1_pk')
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
                )
            ),
            Row(
                Column(
                    'c3_2_no_replacement_criteria_1',
                    css_class='form-group col'
                )
            ),
            Row(
                Column(
                    'c3_2_no_replacement_criteria_2',
                    css_class='form-group col'
                )
            ),
            Row(
                Column(
                    'c3_2_no_replacement_criteria_3',
                    css_class='form-group col'
                )
            ),
            Row(
                Column(
                    PrependedText(
                        'c3_4_no_replacement_refund', '$',
                        min='0', max='1000',
                    ),
                    css_class='form-group col-md-6'
                )
            ),

            Row(
                Column(
                    'c4_1_number_of_replacements',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c4_1_replacement_period',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'c4_1_replacement_after_min_working_days',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c4_1_5_replacement_deadline',
                    css_class='form-group col-md-6'
                )
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
                )
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
                )
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
                )
            ),
            Row(
                Column(
                    'c5_3_2_cannot_transfer_refund_within',
                    css_class='form-group col-md-6'
                )
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
                )
            ),

            Row(
                Column(
                    'c9_1_independent_mediator_1',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'c9_2_independent_mediator_2',
                    css_class='form-group col-md-6'
                )
            ),

            Row(
                Column(
                    'c13_termination_notice',
                    css_class='form-group col-md-6'
                )
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
                )
            ),

            # Submit
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'servicefee_update_route' level_1_pk %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                )
            )
        )

class DocSafetyAgreementForm(forms.ModelForm):
    class Meta:
        model = models.DocSafetyAgreement
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.authority = kwargs.pop('authority')
        self.level_1_pk = kwargs.pop('level_1_pk')
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
                )
            ),
            Row(
                Column(
                    'window_exterior_location',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'grilles_installed_require_cleaning',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'adult_supervision',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'verifiy_employer_understands_window_cleaning',
                    css_class='form-group col-md-6'
                )
            ),

            # Submit
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'case_status_update_route' level_1_pk %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                )
            )
        )

    def clean(self):
        window_exterior_location_verbose_name = models.DocSafetyAgreement._meta.get_field('window_exterior_location').verbose_name
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
        
        grilles_installed_verbose_name = models.DocSafetyAgreement._meta.get_field('grilles_installed_require_cleaning').verbose_name
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
        
        adult_supervision_verbose_name = models.DocSafetyAgreement._meta.get_field('adult_supervision').verbose_name
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
        
        verifiy_employer_understands_verbose_name = models.DocSafetyAgreement._meta.get_field('verifiy_employer_understands_window_cleaning').verbose_name
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

class DocUploadForm(forms.ModelForm):
    class Meta:
        model = models.DocUpload
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.authority = kwargs.pop('authority')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(
                """
                <h5 class="doc-section-header" id="id-doc-upload">Upload Documents</h5>
            """),
            Row(
                Column(
                    'job_order_pdf',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'ipa_pdf',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    'e_issuance_pdf',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'medical_report_pdf',
                    css_class='form-group col-md-6'
                )
            ),
            
            # Submit
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'safetyagreement_update_route' level_1_pk %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                )
            )
        )

class CaseStatusForm(forms.ModelForm):
    class Meta:
        model = models.CaseStatus
        exclude = ['employer_doc']

    def __init__(self, *args, **kwargs):
        self.user_pk = kwargs.pop('user_pk')
        self.authority = kwargs.pop('authority')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('''
                <h3>Case Status</h3>
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
                )
            ),
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'serviceagreement_update_route' level_1_pk %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                )
            )
        )

# Signature Forms
class SignatureForm(forms.ModelForm):
    class Meta:
        model = models.CaseSignature
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
                        Column(field, css_class='form-group col-md-6')
                    )
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
                )
            )
        )
        # Label for signature pad
        self.helper.layout.append(
            Row(
                Column(
                    HTML("""
                        <h6>{{ model_field_verbose_name }}</h6>
                    """)
                )
            )
        )
        # Submit form and clear signature pad buttons
        self.helper.layout.append(
            Row(
                Column(
                    Submit("submit", "Submit"),
                    StrictButton("Clear", onclick="signaturePad.clear()", css_class="btn btn-secondary"),
                )
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

class TokenChallengeForm(forms.Form):
    nric_fin = forms.CharField(label='Last Four Characters of NRIC/FIN', max_length=4)
    mobile = forms.CharField(label='Mobile Phone Number', max_length=8)

    def __init__(self, *args, **kwargs):
        self.object = kwargs.pop('object')
        self.stakeholder = kwargs.pop('stakeholder')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'nric_fin',
                    css_class='form-group col-9 my-2',
                ),
                Column(
                    'mobile',
                    css_class='form-group col-9 my-2',
                ),
                Column(
                    Submit(
                        'submit',
                        'Confirm',
                        css_class="btn btn-primary w-75",
                    ),
                    css_class='form-group col-9 my-3 text-center',
                )
            )
        )
    
    def clean_nric_fin(self):
        cleaned_field = self.cleaned_data.get('nric_fin', '').upper()
        valid = False
        if self.stakeholder == 'employer_1':
            obj = self.object.employer_doc.employer
            if (
                obj.employer_residential_status == constants.ResidentialStatusFullChoices.SC or
                obj.employer_residential_status == constants.ResidentialStatusFullChoices.PR
            ):
                if cleaned_field == obj.get_employer_nric_partial(padded=False):
                    valid = True
            else:
                if cleaned_field == obj.get_employer_fin_partial(padded=False):
                    valid = True

        elif self.stakeholder == 'sponsor_1':
            obj = self.object.employer_doc.employer.rn_sponsor_employer
            if cleaned_field == obj.get_sponsor_1_nric_partial(padded=False):
                valid = True

        elif self.stakeholder == 'sponsor_2':
            obj = self.object.employer_doc.employer.rn_sponsor_employer
            if cleaned_field == obj.get_sponsor_2_nric_partial(padded=False):
                valid = True

        elif self.stakeholder == 'joint_applicant':
            obj = self.object.employer_doc.employer.rn_ja_employer
            if cleaned_field == obj.get_joint_applicant_nric_partial(padded=False):
                valid = True
        
        return cleaned_field if valid else None

    def clean_mobile(self):
        cleaned_field = self.cleaned_data.get('mobile')
        valid = False
        if self.stakeholder == 'employer_1':
            obj = self.object.employer_doc.employer
            if cleaned_field == obj.employer_mobile_number: 
                valid = True

        elif self.stakeholder == 'sponsor_1':
            obj = self.object.employer_doc.employer.rn_sponsor_employer
            if cleaned_field == obj.sponsor_1_mobile_number:
                valid = True

        elif self.stakeholder == 'sponsor_2':
            obj = self.object.employer_doc.employer.rn_sponsor_employer
            if cleaned_field == obj.sponsor_2_mobile_number:
                valid = True

        return cleaned_field if valid else None

    def clean(self):
        cleaned_data = super().clean()
        nric_fin = cleaned_data.get('nric_fin')
        mobile = cleaned_data.get('mobile')

        if nric_fin and mobile:
            return cleaned_data
        else:
            error_msg = _('Invalid Credentials')
            raise ValidationError(
                    error_msg,
                    code= 'invalid',
            )

class EmployerSignatureForm(forms.Form):
    employer_signature = forms.CharField(
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            'employer_signature'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <h6>Employer Signature</h6>
                                <canvas
                                    id="employer-signature-pad"
                                    class=""
                                    style="border: 1px solid #d2d2d2"
                                >
                                </canvas>
                                """
                            )
                        )
                    ),
                    Row(
                        Column(
                            Button(
                            'Clear Signatures',
                            'Clear Signatures',
                            css_class='btn btn-outline-secondary w-25 mr-2',
                            css_id='signature-form-clear-button'
                            ),
                            Button(
                                'Confirm',
                                'Confirm',
                                css_class='btn btn-primary w-25 ml-2',
                                css_id='signature-form-submit-button'
                            ),
                            css_class='d-flex justify-content-center mt-4'
                        )
                    )
                ),
                css_class='form-group'
            )
        )

class EmployerWithSpouseSignatureForm(forms.Form):
    employer_signature = forms.CharField(
        widget=forms.HiddenInput()
    )
    employer_spouse_signature = forms.CharField(
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            'employer_signature'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <h6>Employer Signature</h6>
                                <canvas
                                    id="employer-signature-pad"
                                    class=""
                                    style="border: 1px solid #d2d2d2"
                                >
                                </canvas>
                                """
                            )
                        )
                    )
                ),
                Column(
                    Row(
                        Column(
                            'employer_spouse_signature'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <h6>Employer Spouse Signature</h6>
                                <canvas
                                    id="employer-spouse-signature-pad"
                                    class=""
                                    style="border: 1px solid #d2d2d2"
                                >
                                </canvas>
                                """
                            )
                        )
                    )
                ),
                css_class='form-group'
            ),
            Row(
                Column(
                    Button(
                    'Clear Signatures',
                    'Clear Signatures',
                    css_class='btn btn-outline-secondary w-25 mr-2',
                    css_id='signature-form-clear-button'
                    ),
                    Button(
                        'Confirm',
                        'Confirm',
                        css_class='btn btn-primary w-25 ml-2',
                        css_id='signature-form-submit-button'
                    ),
                    css_class='d-flex justify-content-center mt-4'
                )
            )
        )

class SponsorSignatureForm(forms.Form):
    sponsor_signature = forms.CharField(
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            'sponsor_signature'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <h6>Sponsor Signature</h6>
                                <canvas
                                    id="sponsor-signature-pad"
                                    class=""
                                    style="border: 1px solid #d2d2d2"
                                >
                                </canvas>
                                """
                            )
                        )
                    ),
                    Row(
                        Column(
                            Button(
                            'Clear Signatures',
                            'Clear Signatures',
                            css_class='btn btn-outline-secondary w-25 mr-2',
                            css_id='signature-form-clear-button'
                            ),
                            Button(
                                'Confirm',
                                'Confirm',
                                css_class='btn btn-primary w-25 ml-2',
                                css_id='signature-form-submit-button'
                            ),
                            css_class='d-flex justify-content-center mt-4'
                        )
                    )
                ),
                css_class='form-group'
            )
        )

class EmployerWithJointApplicantSignatureForm(forms.Form):
    employer_signature = forms.CharField(
        widget=forms.HiddenInput()
    )

    joint_applicant_signature = forms.CharField(
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            'employer_signature'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <h6>Employer Signature</h6>
                                <canvas
                                    id="employer-signature-pad"
                                    class=""
                                    style="border: 1px solid #d2d2d2"
                                >
                                </canvas>
                                """
                            )
                        )
                    )
                ),
                Column(
                    Row(
                        Column(
                            'joint_applicant_signature'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <h6>Joint Applicant Signature</h6>
                                <canvas
                                    id="joint-application-signature-pad"
                                    class=""
                                    style="border: 1px solid #d2d2d2"
                                >
                                </canvas>
                                """
                            )
                        )
                    )
                ),
                css_class='form-group'
            ),
            Row(
                Column(
                    Button(
                    'Clear Signatures',
                    'Clear Signatures',
                    css_class='btn btn-outline-secondary w-25 mr-2',
                    css_id='signature-form-clear-button'
                    ),
                    Button(
                        'Confirm',
                        'Confirm',
                        css_class='btn btn-primary w-25 ml-2',
                        css_id='signature-form-submit-button'
                    ),
                    css_class='d-flex justify-content-center mt-4'
                )
            )
        )