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
class EmployerBaseCreateForm(forms.ModelForm):
    class Meta:
        model = EmployerBase
        exclude = ['agency_employee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'employer-base-form mt-5 pt-5'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new employer:',
                # Form fields
                'employer_name',
                'employer_email',
                'employer_mobile_number',
            ),
            Submit('submit', 'Submit')

# Generic Forms (forms.Form)
