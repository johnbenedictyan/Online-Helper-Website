# Imports from django
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import InlineCheckboxes
from maid.models import MaidResponsibility

# Imports from local apps
from .fields import MaidResponsibilityChoiceField
from .models import Enquiry 

# Start of Forms

# Forms that inherit from inbuilt Django forms

# Model Forms

# Generic Forms (forms.Form)
class EnquiryForm(forms.ModelForm):
    maid_responsibility = MaidResponsibilityChoiceField(
        queryset=MaidResponsibility.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Enquiry
        exclude = ['employer']
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'placeholder': 'First Name'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'placeholder': 'Last Name'
                }
            ),
            'contact_number': forms.TextInput(
                attrs={
                    'placeholder': 'Contact Number'
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'placeholder': 'Email Address'
                }
            ),
            'no_of_family_members': forms.NumberInput(
                attrs={
                    'placeholder': 'Number of Family Members'
                }
            ),
            'no_of_below_12': forms.NumberInput(
                attrs={
                    'placeholder': 'Number of Children below 12'
                }
            ),
            'no_of_babies': forms.NumberInput(
                attrs={
                    'placeholder': 'Number of Babies'
                }
            ),
            'remarks': forms.Textarea(
                attrs={
                    'rows': 20,
                    'cols': 15
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'first_name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'last_name',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'contact_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'email',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'maid_nationality',
                    css_class='form-group col-md-3'
                ),
                Column(
                    'maid_type',
                    css_class='form-group col-md-3'
                ),
                Column(
                    'maid_age_group',
                    css_class='form-group col-md-3'
                ),
                Column(
                    'rest_days',
                    css_class='form-group col-md-3'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'maid_responsibility',
                    css_class='form-group col-md-4 mt-1'
                ),
                Column(
                    Row(
                        Column(
                            'property_type',
                            css_class='form-group col-6'
                        ),
                        Column(
                            'no_of_family_members',
                            css_class='form-group col-6'
                        ),
                        Column(
                            'no_of_below_12',
                            css_class='form-group col-6'
                        ),
                        Column(
                            'no_of_babies',
                            css_class='form-group col-6'
                        ),
                        css_class='form-row'
                    ),
                    css_class='form-group col-md-8'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'remarks',
                    css_class='form-group col'
                ),
                css_class='form-row'
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
