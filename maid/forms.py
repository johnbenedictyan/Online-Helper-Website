# Imports from django
from django import forms
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from betterforms.multiform import MultiModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import InlineCheckboxes, PrependedText
from agency.models import Agency

# Imports from local apps
from .models import (
    Maid, MaidBiodata, MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare,
    MaidDisabledCare, MaidGeneralHousework, MaidCooking, 
    MaidFoodHandlingPreference, MaidDietaryRestriction, MaidEmploymentHistory
)

# Start of Forms

# Forms that inherit from inbuilt Django forms

# Model Forms
class MaidCreationForm(forms.ModelForm):
    initial_agency_fee_amount = forms.IntegerField(
        required=True,
        initial=0
    )

    initial_agency_fee_description = forms.CharField(
        required=True,
        widget=forms.Textarea()
    )

    class Meta:
        model = Maid
        exclude = [
            'agency', 'created_on', 'updated_on', 'agency_fee_amount',
            'responsibilities'
        ]

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'reference_number',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'maid_type',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'photo',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'salary', '$'
                    ),
                    css_class='form-group col-md-4'
                ),
                Column(
                    PrependedText(
                        'personal_loan_amount', '$'
                    ),
                    css_class='form-group col-md-4'
                ),
                Column(
                    PrependedText(
                        'initial_agency_fee_amount', '$'
                    ),
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'days_off',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'passport_status',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'repatriation_airport',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'initial_agency_fee_description',
                    css_class='form-group col'
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
                        'Create',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        reference_number = cleaned_data.get('reference_numnber')
        try:
            Maid.objects.get(
                agency = Agency.objects.get(
                    pk = self.agency_id
                ),
                reference_number = reference_number
            )
        except Maid.DoesNotExist:
            pass
        else:
            msg = _('A maid with this reference number already exist')
            self.add_error('reference_number', msg)

class MaidUpdateForm(forms.ModelForm):
    class Meta:
        model = Maid
        exclude = ['agency', 'created_on', 'updated_on', 'agency_fee_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'reference_number',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'maid_type',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'photo',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    PrependedText(
                        'salary', '$'
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    PrependedText(
                        'personal_loan_amount', '$'
                    ),
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'days_off',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'passport_status',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'repatriation_airport',
                    css_class='form-group col-md-4'
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
        
class MaidBiodataForm(forms.ModelForm):
    class Meta:
        model = MaidBiodata
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'age',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'country_of_origin',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'place_of_birth',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'address_1',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'address_2',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'height',
                    css_class='form-group col-md'
                ),
                Column(
                    'weight',
                    css_class='form-group col-md'
                ),
                Column(
                    'religion',
                    css_class='form-group col-md'
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

class MaidFamilyDetailsForm(forms.ModelForm):
    class Meta:
        model = MaidFamilyDetails
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'marital_status',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'number_of_children',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'age_of_children',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'number_of_siblings',
                    css_class='form-group col-md-6'
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

class MaidInfantChildCareForm(forms.ModelForm):
    class Meta:
        model = MaidInfantChildCare
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'assessment',
                    css_class='form-group col-md'
                ),
                Column(
                    'willingness',
                    css_class='form-group col-md'
                ),
                Column(
                    'experience',
                    css_class='form-group col-md'
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
                    'other_remarks',
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

class MaidElderlyCareForm(forms.ModelForm):
    class Meta:
        model = MaidElderlyCare
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'assessment',
                    css_class='form-group col-md'
                ),
                Column(
                    'willingness',
                    css_class='form-group col-md'
                ),
                Column(
                    'experience',
                    css_class='form-group col-md'
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
                    'other_remarks',
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

class MaidDisabledCareForm(forms.ModelForm):
    class Meta:
        model = MaidDisabledCare
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'assessment',
                    css_class='form-group col-md'
                ),
                Column(
                    'willingness',
                    css_class='form-group col-md'
                ),
                Column(
                    'experience',
                    css_class='form-group col-md'
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
                    'other_remarks',
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

class MaidGeneralHouseworkForm(forms.ModelForm):
    class Meta:
        model = MaidGeneralHousework
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'assessment',
                    css_class='form-group col-md'
                ),
                Column(
                    'willingness',
                    css_class='form-group col-md'
                ),
                Column(
                    'experience',
                    css_class='form-group col-md'
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
                    'other_remarks',
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

class MaidCookingForm(forms.ModelForm):
    class Meta:
        model = MaidCooking
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'assessment',
                    css_class='form-group col-md'
                ),
                Column(
                    'willingness',
                    css_class='form-group col-md'
                ),
                Column(
                    'experience',
                    css_class='form-group col-md'
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
                    'other_remarks',
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

class MaidFoodHandlingPreferenceForm(forms.ModelForm):
    class Meta:
        model = MaidFoodHandlingPreference
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'preference',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Purchase',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

class MaidDietaryRestrictionForm(forms.ModelForm):
    class Meta:
        model = MaidDietaryRestriction
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'restriction',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Purchase',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

class MaidEmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = MaidEmploymentHistory
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'country',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'work_duties',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'start_date',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'end_date',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Purchase',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

# Generic Forms (forms.Form)