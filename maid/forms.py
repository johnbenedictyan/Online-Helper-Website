# Imports from django
from django import forms
from django.utils.translation import ugettext_lazy as _

# Imports from project-wide files
from onlinemaid.constants import TrueFalseChoices

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import InlineCheckboxes, PrependedText
from agency.models import Agency

# Imports from local apps
from .constants import (
    TypeOfMaidChoices, MaidReligionChoices, MaidLanguageChoices,
    MaidCountryOfOrigin, MaritalStatusChoices, MaidAssessmentChoices,
    MaidCareRemarksChoices
)

from .models import (
    Maid, MaidPersonalDetails, MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare,
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
        model = MaidPersonalDetails
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
class MainMaidCreationForm(forms.Form):
    # Maid Information
    photo = forms.ImageField(
        label='',
        required=True
    )

    reference_number = forms.CharField(
        label='',
        max_length=50,
        required=True
    )

    name = forms.CharField(
        label='',
        max_length=255,
        required=True
    )

    maid_type = forms.ChoiceField(
        label='',
        choices=TypeOfMaidChoices.choices,
        initial=TypeOfMaidChoices.NEW,
        required=True
    )

    days_off = forms.IntegerField(
        label='',
        max_value=30,
        min_value=0,
        required=True
    )

    remarks =  forms.CharField(
        label='',
        widget=forms.Textarea,
        required=True
    )

    # Maid Personal Details
    height = forms.DecimalField(
        max_value=200,
        min_value=0,
        max_digits=5,
        decimal_places=2,
        required=True
    )

    weight = forms.DecimalField(
        max_value=100,
        min_value=0,
        max_digits=5,
        decimal_places=2,
        required=True
    )

    religion = forms.ChoiceField(
        label='',
        choices=MaidReligionChoices.choices,
        initial=MaidReligionChoices.NONE,
        required=True
    )

    language_spoken = forms.MultipleChoiceField(
        label='',
        choices=MaidLanguageChoices.choices,
        required=True
    )

    date_of_birth = forms.DateField(
        label='',
        required=True
    )

    country_of_origin = forms.ChoiceField(
        label='',
        choices=MaidCountryOfOrigin.choices,
        required=True
    )

    address_1 = forms.CharField(
        label='',
        max_length=255,
        required=True
    )

    address_2 = forms.CharField(
        label='',
        max_length=255,
        required=True
    )

    repatriation_airport = forms.CharField(
        label=_('Repatriation airport'),
        max_length=100,
        required=True
    )

    place_of_birth = forms.CharField(
        label=_('Place of birth'),
        max_length=25,
        required=True
    )

    # Maid Family Details
    marital_status = forms.ChoiceField(
        label=_('Marital Status'),
        required=True,
        choices=MaritalStatusChoices.choices,
        initial=MaritalStatusChoices.SINGLE
    )

    number_of_children = forms.IntegerField(
        required=True,
        initial=0,
        max_value=20,
        min_value=0
    )

    age_of_children = forms.CharField(
        label=_('Age of children'),
        max_length=50,
        required=True,
        initial='N.A'
    )

    number_of_siblings = forms.IntegerField(
        required=True,
        initial=0,
        max_value=20,
        min_value=0
    )

    # Care
    cfi_assessment = forms.IntegerField(
        label=_('Infant child care assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfi_willingness = forms.ChoiceField(
        label=_('Willingness for infant child care'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cfi_experience = forms.ChoiceField(
        label=_('Experience with infant child care'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cfi_remarks = forms.ChoiceField(
        label=_('Remarks for infant child care'),
        required=True,
        choices=MaidCareRemarksChoices.choices,
        null=True
    )

    cfi_other_remarks = forms.TextField(
        label=_('Other remarks for infant child care'),
        blank=True
    )

    cfe_assessment = forms.IntegerField(
        label=_('Elderly care assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfe_willingness = forms.ChoiceField(
        label=_('Willingness for elderly care'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        
    )

    cfe_experience = forms.ChoiceField(
        label=_('Experience with elderly care'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
        
    )

    cfe_remarks = forms.ChoiceField(
        label=_('Remarks for elderly care'),
        required=True,
        choices=MaidCareRemarksChoices.choices
    )

    cfe_other_remarks = forms.TextField(
        label=_('Other remarks for elderly care'),
        blank=True
    )
    
    cfd_assessment = forms.IntegerField(
        label=_('Disabled care assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfd_willingness = forms.ChoiceField(
        label=_('Willingness for disabled care'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cfd_experience = forms.ChoiceField(
        label=_('Experience with disabled care'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cfd_remarks = forms.ChoiceField(
        label=_('Remarks for disabled care'),
        required=True,
        choices=MaidCareRemarksChoices.choices,
        null=True
    )

    cfd_other_remarks = forms.TextField(
        label=_('Other remarks for disabled care'),
        blank=True
    )

    geh_assessment = forms.IntegerField(
        label=_('General housework care assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    geh_willingness = forms.ChoiceField(
        label=_('Willingness for general housework care'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    geh_experience = forms.ChoiceField(
        label=_('Experience with general housework care'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    geh_remarks = forms.ChoiceField(
        label=_('Remarks for general housework care'),
        required=True,
        choices=MaidCareRemarksChoices.choices,
        null=True
    )

    geh_other_remarks = forms.TextField(
        label=_('Other remarks for general housework care'),
        blank=True
    )

    cok_assessment = forms.IntegerField(
        label=_('Cooking assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cok_willingness = forms.ChoiceField(
        label=_('Willingness for cooking'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cok_experience = forms.ChoiceField(
        label=_('Experience with cooking'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
        
    )

    cok_remarks = forms.ChoiceField(
        label=_('Remarks for cooking'),
        required=True,
        choices=MaidCareRemarksChoices.choices,
        null=True
    )

    cok_other_remarks = forms.TextField(
        label=_('Other remarks for cooking'),
        blank=True
    )

    # Financial
    initial_agency_fee_amount = forms.DecimalField(
        label=_('Initial agency fee amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=True,
        initial=0
    )

    initial_agency_fee_description = forms.CharField(
        required=True,
        widget=forms.Textarea()
    )

    salary = forms.DecimalField(
        label=_('Salary'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=True,
        initial=0
    )

    personal_loan_amount = forms.DecimalField(
        label=_('Personal loan amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=True,
        initial=0
    )
