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
        self.helper.form_class = 'employer-doc-base-form'
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
        self.helper.form_class = 'employer-doc-base-form'
        self.helper.layout = Layout(
            Fieldset(
                # Legend for form
                'Create new / update existing employer doc base job order:',
                # Form fields
                'job_order_date',
                'employer_race',
                'type_of_property_choices',
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



# Generic Forms (forms.Form)
