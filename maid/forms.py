# Python
import re

# Imports from django
from django import forms
from django.forms import formset_factory, inlineformset_factory
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Imports from project-wide files
from onlinemaid.constants import TrueFalseChoices

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, InlineCheckboxes
from agency.models import Agency

# Imports from local apps
from .constants import (
    TypeOfMaidChoices, MaidReligionChoices, MaidLanguageChoices,
    MaidCountryOfOrigin, MaritalStatusChoices, MaidAssessmentChoices,
    MaidCareRemarksChoices, MaidPassportStatusChoices, 
    MaidEducationLevelChoices, MaidSkillsEvaluationMethod
)

from .models import (
    Maid, MaidFinancialDetails, MaidLanguage, MaidPersonalDetails, 
    MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare, MaidDisabledCare, 
    MaidGeneralHousework, MaidCooking, MaidFoodHandlingPreference, 
    MaidDietaryRestriction, MaidEmploymentHistory, MaidAgencyFeeTransaction,
    MaidOtherCare, MaidFinancialDetails
)
from agency.models import Agency
from onlinemaid.helper_functions import encrypt_string, decrypt_string

# Utility functions
def validate_passport_number(cleaned_field, max_length=None):
    if not isinstance(cleaned_field, str):
        raise ValidationError('Must be a string')

    if not re.match('^[A-Za-z0-9]*$', cleaned_field):
        raise ValidationError('Can only enter letters or numbers')

    if max_length:
        if len(cleaned_field)>max_length:
            raise ValidationError(f'Must not exceed {max_length} characters')


from .widgets import CustomDateInput

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
            'responsibilities', 'nonce', 'tag'
        ]

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id')
        super().__init__(*args, **kwargs)

        self.FIELD_MAXLENGTH = 20

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'reference_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'maid_type',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Field(
                        'passport_number',
                        maxlength=self.FIELD_MAXLENGTH,
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'photo',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row form-group'
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

    def clean_reference_number(self):
        reference_number = self.cleaned_data.get('reference_number')
        try:
            Maid.objects.get(
                agency = Agency.objects.get(
                    pk = self.agency_id
                ),
                reference_number = reference_number
            )
        except Maid.DoesNotExist:
            return reference_number
        else:
            msg = _('A maid with this reference number already exists')
            self.add_error('reference_number', msg)

    def clean_passport_number(self):
        cleaned_field = self.cleaned_data.get('passport_number')

        # If form errors then raise ValidationError, else continue
        validate_passport_number(cleaned_field, self.FIELD_MAXLENGTH)

        # Encryption
        ciphertext, self.instance.nonce, self.instance.tag = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )

        return ciphertext

class MaidUpdateForm(forms.ModelForm):
    class Meta:
        model = Maid
        exclude = ['agency', 'created_on', 'updated_on', 'agency_fee_amount',
            'responsibilities', 'nonce', 'tag'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.FIELD_MAXLENGTH = 20

        ###################################################################################################### TO BE REMOVED
        '''
        Decryption
        '''
        if self.instance.passport_number and self.instance.passport_number!=b'':
            try:
                plaintext = decrypt_string(self.instance.passport_number, settings.ENCRYPTION_KEY, self.instance.nonce, self.instance.tag)
                self.initial.update({'passport_number': plaintext})
            except (ValueError, KeyError):
                print("Incorrect decryption")
                self.initial.update({'passport_number': ''})
        ###################################################################################################### TO BE REMOVED

        #  Remove passport number from initial form display
        # self.initial.update({'passport_number':''})
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'reference_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'maid_type',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Field(
                        'passport_number',
                        maxlength=self.FIELD_MAXLENGTH,
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    'photo',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row form-group'
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
 
    def clean_reference_number(self):
        reference_number = self.cleaned_data.get('reference_number')
        try:
            maid = Maid.objects.get(
                agency = Agency.objects.get(
                    pk = self.instance.agency.pk
                ),
                reference_number = reference_number
            )
        except Maid.DoesNotExist:
            return reference_number
        else:
            if maid.pk==self.instance.pk:
                return reference_number
            else:
                msg = _('A maid with this reference number already exists')
                self.add_error('reference_number', msg)
       
    def clean_passport_number(self):
        cleaned_field = self.cleaned_data.get('passport_number')

        # If form errors then raise ValidationError, else continue
        validate_passport_number(cleaned_field, self.FIELD_MAXLENGTH)

        # Encryption
        ciphertext, self.instance.nonce, self.instance.tag = encrypt_string(
            cleaned_field,
            settings.ENCRYPTION_KEY
        )

        return ciphertext

class MaidPersonalDetailsForm(forms.ModelForm):
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
                    AppendedText(
                        'height', 'cm'
                    ),
                    css_class='form-group col-md'
                ),
                Column(
                    AppendedText(
                        'weight', 'kg'
                    ),
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

class MaidFinancialDetailsForm(forms.ModelForm):
    class Meta:
        model = MaidFinancialDetails
        exclude = ['maid']

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

MaidEmploymentHistoryFormSet = inlineformset_factory(
    parent_model = Maid,
    model = MaidEmploymentHistory,
    fields = ['country','start_date','end_date','work_duties',]
)

class MaidEmploymentHistoryFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            HTML('''
                <h5>Past employment {{ forloop.counter }}</h5>
            '''),
            Row(
                Column(
                    Row(
                        Column(
                            'country',
                            css_class='form-group col-12'
                        ),
                        Column(
                            Field(
                                'start_date',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Past employment start date'
                            ),
                            css_class='form-group col-12'
                        ),
                        Column(
                            Field(
                                'end_date',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Past employment end date'
                            ),
                            css_class='form-group col-12'
                        ),
                    ),
                    css_class='form-group col-md-6'
                ),
                Column(
                    InlineCheckboxes('work_duties'),
                    css_class='form-group col-md-6 work-duties'
                ),
                css_class='form-row'
            ),
            HTML('<hr>'),
        )
        self.render_required_fields = True

class MaidAgencyFeeTransactionForm(forms.ModelForm):
    class Meta:
        model = MaidAgencyFeeTransaction
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'amount',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'transaction_type',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'transaction_date',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'description',
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

# Generic Forms (forms.Form)
class MainMaidCreationForm(forms.Form):
    # Maid Information
    photo = forms.ImageField(
        label=_('Photo'),
        required=True
    )

    reference_number = forms.CharField(
        label='Reference Number',
        max_length=50,
        required=True
    )

    name = forms.CharField(
        label='Name',
        max_length=255,
        required=True
    )

    maid_type = forms.ChoiceField(
        label='Type of Maid',
        choices=TypeOfMaidChoices.choices,
        initial=TypeOfMaidChoices.NEW,
        required=True
    )

    days_off = forms.IntegerField(
        label='No of day off',
        max_value=30,
        min_value=0,
        required=True
    )
    
    passport_number = forms.CharField(
        label='Passport Number',
        max_length=20,
        required=True
    )
    
    passport_status = forms.ChoiceField(
        label='Passport Status',
        choices=MaidPassportStatusChoices.choices,
        initial=MaidPassportStatusChoices.NOT_READY
    )

    remarks = forms.CharField(
        label=_('Remarks'),
        widget=forms.Textarea(attrs={
            'maxlength': '300'    
        }),
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
        label=_('Religion'),
        choices=MaidReligionChoices.choices,
        initial=MaidReligionChoices.NONE,
        required=True
    )

    language_spoken = forms.MultipleChoiceField(
        label=_('Language Spoken'),
        choices=MaidLanguageChoices.choices,
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )

    preferred_language = forms.ChoiceField(
        label=_('Preferred Language'),
        choices=MaidLanguageChoices.choices,
        required=True
    )

    date_of_birth = forms.DateField(
        label=_('Date of Birth'),
        required=True,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )

    country_of_origin = forms.ChoiceField(
        label=_('Country of Origin'),
        choices=MaidCountryOfOrigin.choices,
        required=True
    )

    address_1 = forms.CharField(
        label='Address Line 1',
        max_length=255,
        required=True
    )

    address_2 = forms.CharField(
        label='Address Line 2',
        max_length=255,
        required=True
    )

    repatriation_airport = forms.CharField(
        label='Repatriation Airport',
        max_length=100,
        required=True
    )

    place_of_birth = forms.CharField(
        label='Place of Birth',
        max_length=25,
        required=True
    )
    
    contact_number = forms.CharField(
        label=_('Contact Number'),
        max_length=30,
        required=True
    )

    education_level = forms.ChoiceField(
        label=_('Education Level'),
        required=True,
        choices=MaidEducationLevelChoices.choices,
        initial=MaidEducationLevelChoices.HIGH_SCHOOL
    )
    
    # Maid Family Details
    marital_status = forms.ChoiceField(
        label='Marital Status',
        required=True,
        choices=MaritalStatusChoices.choices,
        initial=MaritalStatusChoices.SINGLE
    )

    number_of_children = forms.IntegerField(
        label='Number of Children',
        required=True,
        initial=0,
        max_value=20,
        min_value=0
    )

    age_of_children = forms.CharField(
        label='Age of Children',
        max_length=50,
        required=True,
        initial='N.A'
    )

    number_of_siblings = forms.IntegerField(
        label='Number of Siblings',
        required=True,
        initial=0,
        max_value=20,
        min_value=0
    )

    # Food Handling Preferences and Dietary Restrictions
    food_handling_pork = forms.ChoiceField(
        label=_('Can you handle pork'),
        required=True,
        choices=TrueFalseChoices('Yes', 'No')
    )
    
    food_handling_beef = forms.ChoiceField(
        label=_('Can you handle beef'),
        required=True,
        choices=TrueFalseChoices('Yes', 'No')
    )
    
    food_handling_veg = forms.ChoiceField(
        label=_('Are you willing to work in a vegetarian family'),
        required=True,
        choices=TrueFalseChoices('Yes', 'No')
    )
    
    dietary_restriction_pork = forms.ChoiceField(
        label=_('Can you eat pork'),
        required=True,
        choices=TrueFalseChoices('Yes', 'No')
    )
    
    dietary_restriction_beef = forms.ChoiceField(
        label=_('Can you eat beef'),
        required=True,
        choices=TrueFalseChoices('Yes', 'No')
    )
    
    dietary_restriction_veg = forms.ChoiceField(
        label=_('Are you a vegetarian'),
        required=True,
        choices=TrueFalseChoices('Yes', 'No')
    )
    
    # Care
    skills_evaluation_method = forms.ChoiceField(
        label=_('Skills evaluation method'),
        required=True,
        choices=MaidSkillsEvaluationMethod.choices,
        initial=MaidSkillsEvaluationMethod.DECLARATION
    )
    
    cfi_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,  
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfi_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cfi_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cfi_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=False,
        choices=MaidCareRemarksChoices.choices,
    )

    cfi_other_remarks = forms.CharField(
        label=_('Other remarks'),
        max_length=80,
        required=False
    )

    cfe_assessment = forms.ChoiceField(
        label=_('Elderly care assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfe_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        
    )

    cfe_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
        
    )

    cfe_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=MaidCareRemarksChoices.choices
    )

    cfe_other_remarks = forms.CharField(
        label=_('Other remarks'),
        max_length=80,
        required=False
    )
    
    cfd_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfd_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cfd_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cfd_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=MaidCareRemarksChoices.choices,
    )

    cfd_other_remarks = forms.CharField(
        label=_('Other remarks'),
        max_length=80,
        required=False
    )

    geh_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    geh_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    geh_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    geh_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=MaidCareRemarksChoices.choices
    )

    geh_other_remarks = forms.CharField(
        label=_('Other remarks'),
        max_length=80,
        required=False
    )

    cok_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cok_willingness = forms.ChoiceField(
        label=_('Willingness '),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cok_experience = forms.ChoiceField(
        label=_('Experience '),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cok_remarks = forms.ChoiceField(
        label=_('Remarks '),
        required=True,
        choices=MaidCareRemarksChoices.choices,
    )

    cok_other_remarks = forms.CharField(
        label=_('Other remarks '),
        max_length=80,
        required=False
    )
    
    care_for_pets = forms.ChoiceField(
        label=_('Care for pets'),
        required=True,
        choices=TrueFalseChoices('Able', 'Unable')
    )
    
    gardening = forms.ChoiceField(
        label=_('Gardening'),
        required=True,
        choices=TrueFalseChoices('Able', 'Unable')
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
        label=_('Base Salary'),
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

    transaction_date = forms.DateField(
        label=_('Date'),
        required=True,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )

    # Override Field for the checking of duplicate fdws
    override = forms.BooleanField(
        widget=forms.HiddenInput(),
        initial=False
    )

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    HTML(
                        '<h4>Maid Photo</h4>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    HTML(
                        "<img src='{{ MEDIA_URL }}{% if form.photo.value%}{{form.photo.value}}{% else %}/thumbnails/default{% endif %}' alt='' class='img-fluid thumbnail' >"
                    ),
                    'photo',
                    css_class='form-group col-md-6'
                )
            ),
            Row(
                Column(
                    HTML(
                        '<h4>Maid Information</h4>'
                    ),
                    css_class=''
                ),
                css_class=''
            ),
            Div(
                Column(
                    'reference_number',
                    css_class='col-md-6'
                ),
                Column(
                    'name',
                    css_class='col-md-6'
                ),
                Column(
                    'country_of_origin',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_type',
                    css_class='col-md-6'
                ),
                Column(
                    '',
                    css_class='col-md-6'
                ),
                Column(
                    'days_off',
                    css_class='col-md-6'
                ),
                Column(
                    'passport_status',
                    css_class='col-md-6'
                ),
                Column(
                    'passport_number',
                    css_class='col-md-6'
                ),
                Column(
                    'passport_status',
                    css_class='col-md-6'
                ),
                Column(
                    'passport_number',
                    css_class='col-md-6'
                ),
                Column(
                    'contact_number',
                    css_class='col-md-6'
                ),
                css_class='row form-group'
            ),
            Row(
                Column(
                    HTML(
                        '<h4>Personal Details</h4>'
                    ),
                    css_class='col'
                ),
                css_class='row'
            ),
            Div(
                Column(
                    'date_of_birth',
                    css_class='col-md-6'
                ),
                Column(
                    'age',
                    css_class='col-md-6'
                ),
                Column(
                    'height',
                    css_class='col-md-6'
                ),
                Column(
                    'weight',
                    css_class='col-md-6'
                ),
                Column(
                    'marital_status',
                    css_class='col-md-6'
                ),
                Column(
                    'number_of_siblings',
                    css_class='col-md-6'
                ),
                Column(
                    'number_of_children',
                    css_class='col-md-6'
                ),
                Column(
                    'age_of_children',
                    css_class='col-md-6'
                ),
                Column(
                    'religion',
                    css_class='col-md-6'
                ),
                Column(
                    'place_of_birth',
                    css_class='col-md-6'
                ),
                Column(
                    'address_1',
                    css_class='col-md-6'
                ),
                Column(
                    'address_2',
                    css_class='col-md-6'
                ),
                Column(
                    'repatriation_airport',
                    css_class='col-md-6'
                ),
                css_class='row form-group'
            ),
            Row(
                Column(
                    HTML(
                        '<h4>Language Spoken</h4>'
                    ),
                    css_class='col'
                ),
                css_class='row'
            ),
            Row(
                Column(
                    Field(
                        'language_spoken',
                        template='widgets/custom-inline-checkbox.html'
                    ),
                    css_class='form-row'
                ),
                css_class='form-group'
            ),
            Row(
                Column(
                    HTML(
                        '<h4>Food Handling and Dietary Restriction</h4>'
                    ),
                    css_class='col'
                ),
                css_class='row'
            ),
            Row(
                Column(
                    'food_handling_pork',
                    css_class='col-md-6'
                ),
                Column(
                    'dietary_restriction_pork',
                    css_class='col-md-6'
                ),
                Column(
                    'food_handling_beef',
                    css_class='col-md-6'
                ),
                Column(
                    'dietary_restriction_beef',
                    css_class='col-md-6'
                ),
                Column(
                    'dietary_restriction_veg',
                    css_class='col-md-6'
                ),
                Column(
                    'food_handling_veg',
                    css_class='col-md-6'
                ),
                css_class='form-group'
            ),
            Row(
                Column(
                    HTML(
                        '<h4>Experience</h4>'
                    ),
                    css_class='col'
                ),
                css_class='row'
            ),
            Row(
                Column(
                    HTML(
                        '<h6>Infant Child Care</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    Row(
                        Column(
                            'cfi_willingness',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cfi_assessment',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                    Row(
                        Column(
                            'cfi_remarks',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cfi_other_remarks',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                ),
                css_class='row'
            ),
            Row(
                Column(
                    HTML(
                        '<h6>Elderly Care</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    Row(
                        Column(
                            'cfe_willingness',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cfe_assessment',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                    Row(
                        Column(
                            'cfe_remarks',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cfe_other_remarks',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                ),
                css_class='row'
            ),
            Row(
                Column(
                    HTML(
                        '<h6>Disabled Care</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    Row(
                        Column(
                            'cfd_willingness',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cfd_assessment',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                    Row(
                        Column(
                            'cfd_remarks',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cfd_other_remarks',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                ),
                css_class='row'
            ),
            Row(
                Column(
                    HTML(
                        '<h6>General Housework</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    Row(
                        Column(
                            'geh_willingness',
                            css_class='col-md-6'
                        ),
                        Column(
                            'geh_assessment',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                    Row(
                        Column(
                            'geh_remarks',
                            css_class='col-md-6'
                        ),
                        Column(
                            'geh_other_remarks',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                ),
                css_class='row'
            ),
            Row(
                Column(
                    HTML(
                        '<h6>Cooking</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    Row(
                        Column(
                            'cok_willingness',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cok_assessment',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                    Row(
                        Column(
                            'cok_remarks',
                            css_class='col-md-6'
                        ),
                        Column(
                            'cok_other_remarks',
                            css_class='col-md-6'
                        ),
                        css_class='form-group'
                    ),
                ),
                css_class='row'
            ),
            Row(
                Column(
                    HTML(
                        '<h4>Maid Loan</h4>'
                    ),
                    css_class='col'
                ),
                css_class='row'
            ),
            Row(
                Column(
                    'salary',
                    css_class='col-md-6'
                ),
                Column(
                    'personal_loan_amount',
                    css_class='col-md-6'
                )
            ),
            Row(
                Column(
                    'initial_agency_fee_amount',
                    css_class='col-md-6'
                ),
                Column(
                    'transaction_date',
                    css_class='col-md-6'
                ),
                Column(
                    'initial_agency_fee_description',
                    css_class='form-group col-12'
                )
            ),
            Row(
                Column(
                    HTML(
                        '<h4>Other Remarks</h4>'
                    ),
                    css_class='col'
                ),
                css_class='row'
            ),
            Row(
                Column(
                    'remarks',
                    css_class='col-12 form-row'
                ),
                css_class='form-group'
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

    def clean_reference_number(self):
        reference_number = self.cleaned_data.get('reference_number')
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

        return reference_number

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get('passport_number')
        validate_passport_number(passport_number)
        return passport_number

    def clean_preferred_language(self):
        preferred_language = self.cleaned_data.get('preferred_language')
        language_spoken = self.cleaned_data.get('language_spoken')
        if preferred_language not in language_spoken:
            self.add_error(
                'preferred_language',
                _('FDW must be able to speak this language')
            ) 
        return preferred_language

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number.isnumeric() == False:
            self.add_error(
                'contact_number',
                _('Contact Number must be a number')
            ) 
        return contact_number
    
    def clean_cfi_other_remarks(self):
        cfi_remarks = self.cleaned_data.get('cfi_remarks')
        cfi_other_remarks = self.cleaned_data.get('cfi_other_remarks')
        if cfi_remarks == 'OTH' and cfi_other_remarks == '':
            self.add_error(
                'cfi_other_remarks',
                _('Please specify the remarks')
            )

    def clean_cfe_other_remarks(self):
        cfe_remarks = self.cleaned_data.get('cfe_remarks')
        cfe_other_remarks = self.cleaned_data.get('cfe_other_remarks')
        if cfe_remarks == 'OTH' and cfe_other_remarks == '':
            self.add_error(
                'cfe_other_remarks',
                _('Please specify the remarks')
            )

    def clean_cfd_other_remarks(self):
        cfd_remarks = self.cleaned_data.get('cfd_remarks')
        cfd_other_remarks = self.cleaned_data.get('cfd_other_remarks')
        if cfd_remarks == 'OTH' and cfd_other_remarks == '':
            self.add_error(
                'cfd_other_remarks',
                _('Please specify the remarks')
            )

    def clean_geh_other_remarks(self):
        geh_remarks = self.cleaned_data.get('geh_remarks')
        geh_other_remarks = self.cleaned_data.get('geh_other_remarks')
        if geh_remarks == 'OTH' and geh_other_remarks == '':
            self.add_error(
                'geh_other_remarks',
                _('Please specify the remarks')
            )

    def clean_cok_other_remarks(self):
        cok_remarks = self.cleaned_data.get('cok_remarks')
        cok_other_remarks = self.cleaned_data.get('cok_other_remarks')
        if cok_remarks == 'OTH' and cok_other_remarks == '':
            self.add_error(
                'cok_other_remarks',
                _('Please specify the remarks')
            )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        raw_passport_number = cleaned_data.get('passport_number')
        date_of_birth = cleaned_data.get('date_of_birth')
        country_of_origin = cleaned_data.get('country_of_origin')
        place_of_birth = cleaned_data.get('place_of_birth')
        encrypted_passport_number, nonce, tag = encrypt_string(
            raw_passport_number,
            settings.ENCRYPTION_KEY
        )
        override = cleaned_data.get('override')
        possible_duplicate_maids = Maid.objects.filter(
            agency__pk=self.agency_id,
            name__trigram_similar = name,
            date_of_birth = date_of_birth,
            country_of_origin = country_of_origin,
            place_of_birth__trigram_similar = place_of_birth
        )
        # This value 3 should be a threshold settings
        if possible_duplicate_maids.count() < 3 and override != True:
            msg = "This FDW looks similar to these other fdws: "
            for i in possible_duplicate_maids:
                msg += f"""
                    <a href="{reverse_lazy('maid_update', pk=i.pk)}" 
                    target="_blank">
                    {i.name}
                    </a>
                """
            self.data['override'] = True
            self.add_error(None, msg)

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        
        # Encrypting the passport number
        raw_passport_number = cleaned_data.get('passport_number')
        encrypted_passport_number, nonce, tag = encrypt_string(
            raw_passport_number,
            settings.ENCRYPTION_KEY
        )
        try:
            new_maid = Maid.objects.create(
                agency=Agency.objects.get(
                    pk=self.agency_id
                ),
                reference_number=cleaned_data.get('reference_number'),
                name=cleaned_data.get('name'),
                passport_number=encrypted_passport_number,
                nonce=nonce,
                tag=tag,
                photo=cleaned_data.get('photo'),
                maid_type=cleaned_data.get('maid_type'),
                days_off=cleaned_data.get('days_off'),
                passport_status=cleaned_data.get('passport_status'),
                remarks=cleaned_data.get('remarks'),
                skills_evaluation_method=cleaned_data.get(
                    'skills_evaluation_method'
                )
            )
        except Exception as e:
            raise Exception
        else:
            new_maid_personal_details = MaidPersonalDetails.objects.create(
                maid=new_maid,
                date_of_birth=cleaned_data.get('date_of_birth'),
                age=cleaned_data.get('age'),
                country_of_origin=cleaned_data.get('country_of_origin'),
                height=cleaned_data.get('height'),
                weight=cleaned_data.get('weight'),
                place_of_birth=cleaned_data.get('place_of_birth'),
                address_1=cleaned_data.get('address_1'),
                address_2=cleaned_data.get('address_2'),
                repatriation_airport=cleaned_data.get('repatriation_airport'),
                religion=cleaned_data.get('religion'),
                preferred_language=MaidLanguage.objects.get(
                    language=cleaned_data.get('preferred_language')
                ),
                contact_number=cleaned_data.get('contact_number'),
                education_level=cleaned_data.get('education_level')
            )
            for language in cleaned_data.get('language_spoken'):
                new_maid_personal_details.languages.add(
                    MaidLanguage.objects.get(
                        language=language
                    )
                )
            MaidFamilyDetails.objects.create(
                maid=new_maid,
                marital_status=cleaned_data.get('marital_status'),
                number_of_children=cleaned_data.get('number_of_children'),
                age_of_children=cleaned_data.get('age_of_children'),
                number_of_siblings=cleaned_data.get('number_of_siblings')
            )
            MaidFinancialDetails.objects.create(
                maid=new_maid,
                salary=cleaned_data.get('salary'),
                personal_loan_amount=cleaned_data.get('personal_loan_amount')
            )
            MaidInfantChildCare.objects.create(
                maid=new_maid,
                assessment=cleaned_data.get('cfi_assessment'),
                willingness=cleaned_data.get('cfi_willingness'),
                experience=cleaned_data.get('cfi_experience'),
                remarks=cleaned_data.get('cfi_remarks'),
                other_remarks=cleaned_data.get('cfi_other_remarks')
            )
            MaidElderlyCare.objects.create(
                maid=new_maid,
                assessment=cleaned_data.get('cfe_assessment'),
                willingness=cleaned_data.get('cfe_willingness'),
                experience=cleaned_data.get('cfe_experience'),
                remarks=cleaned_data.get('cfe_remarks'),
                other_remarks=cleaned_data.get('cfe_other_remarks')
            )
            MaidDisabledCare.objects.create(
                maid=new_maid,
                assessment=cleaned_data.get('cfd_assessment'),
                willingness=cleaned_data.get('cfd_willingness'),
                experience=cleaned_data.get('cfd_experience'),
                remarks=cleaned_data.get('cfd_remarks'),
                other_remarks=cleaned_data.get('cfd_other_remarks')
            )
            MaidGeneralHousework.objects.create(
                maid=new_maid,
                assessment=cleaned_data.get('geh_assessment'),
                willingness=cleaned_data.get('geh_willingness'),
                experience=cleaned_data.get('geh_experience'),
                remarks=cleaned_data.get('geh_remarks'),
                other_remarks=cleaned_data.get('geh_other_remarks')
            )
            MaidCooking.objects.create(
                maid=new_maid,
                assessment=cleaned_data.get('cok_assessment'),
                willingness=cleaned_data.get('cok_willingness'),
                experience=cleaned_data.get('cok_experience'),
                remarks=cleaned_data.get('cok_remarks'),
                other_remarks=cleaned_data.get('cok_other_remarks')
            )
            MaidOtherCare.objects.create(
                maid=new_maid,
                care_for_pets=cleaned_data.get('care_for_pets'),
                gardening=cleaned_data.get('gardening')
            )
            MaidAgencyFeeTransaction.objects.create(
                maid=new_maid,
                amount=cleaned_data.get('initial_agency_fee_amount'),
                transaction_type='ADD',
                description=cleaned_data.get('initial_agency_fee_description'),
                transaction_date=cleaned_data.get('transaction_date')
            )
        finally:
            return new_maid

class MaidCareForm(forms.Form):
    skills_evaluation_method = forms.ChoiceField(
        label=_('Skills evaluation method'),
        required=True,
        choices=MaidSkillsEvaluationMethod.choices,
        initial=MaidSkillsEvaluationMethod.DECLARATION
    )
    
    cfi_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfi_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cfi_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cfi_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=False,
        choices=MaidCareRemarksChoices.choices,
    )

    cfi_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=forms.Textarea,
        required=False
    )

    cfe_assessment = forms.ChoiceField(
        label=_('Elderly care assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfe_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
        
    )

    cfe_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
        
    )

    cfe_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=MaidCareRemarksChoices.choices
    )

    cfe_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=forms.Textarea,
        required=False
    )
    
    cfd_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfd_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cfd_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cfd_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=MaidCareRemarksChoices.choices,
    )

    cfd_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=forms.Textarea,
        required=False
    )

    geh_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    geh_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    geh_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    geh_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=MaidCareRemarksChoices.choices
    )

    geh_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=forms.Textarea,
        required=False
    )

    cok_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cok_willingness = forms.ChoiceField(
        label=_('Willingness '),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing'),
    )

    cok_experience = forms.ChoiceField(
        label=_('Experience '),
        required=True,
        choices=TrueFalseChoices('Experience', 'No experience'),
    )

    cok_remarks = forms.ChoiceField(
        label=_('Remarks '),
        required=True,
        choices=MaidCareRemarksChoices.choices,
    )

    cok_other_remarks = forms.CharField(
        label=_('Other remarks '),
        widget=forms.Textarea,
        required=False
    )
    
    care_for_pets = forms.ChoiceField(
        label=_('Care for pets'),
        required=True,
        choices=TrueFalseChoices('Able', 'Unable')
    )
    
    gardening = forms.ChoiceField(
        label=_('Gardening'),
        required=True,
        choices=TrueFalseChoices('Able', 'Unable')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'skills_evaluation_method'
                )
            ),
            Div(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5>Infant Child Care</h5>'
                            ),
                            css_class='col-12'
                        ),
                        Column(
                            'cfi_assessment',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfi_willingness',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfi_experience',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfi_remarks',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfi_other_remarks',
                            css_class='form-group'
                        )
                    ),
                    css_class='col-lg-6'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5>Elderly Care</h5>'
                            ),
                            css_class='col-12'
                        ),
                        Column(
                            'cfe_assessment',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfe_willingness',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfe_experience',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfe_remarks',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfe_other_remarks',
                            css_class='form-group'
                        )
                    ),
                    css_class='col-lg-6'
                ),
                css_class='row'
            ),
            Div(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5>Disabled Care</h5>'
                            ),
                            css_class='col-12'
                        ),
                        Column(
                            'cfd_assessment',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfd_willingness',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfd_experience',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfd_remarks',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cfd_other_remarks',
                            css_class='form-group'
                        )
                    ),
                    css_class='col-lg-6'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5>General Housework</h5>'
                            ),
                            css_class='col-12'
                        ),
                        Column(
                            'geh_assessment',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'geh_willingness',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'geh_experience',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'geh_remarks',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'geh_other_remarks',
                            css_class='form-group'
                        )
                    ),
                    css_class='col-lg-6'
                ),
                css_class='row'
            ),
            Div(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5>Cooking</h5>'
                            ),
                            css_class='col-12'
                        ),
                        Column(
                            'cok_assessment',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cok_willingness',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cok_experience',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cok_remarks',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'cok_other_remarks',
                            css_class='form-group'
                        )
                    ),
                    css_class='col-lg-6'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5>Other Care</h5>'
                            ),
                            css_class='col-12'
                        ),
                        Column(
                            'care_for_pets',
                            css_class='form-group col-md-6'
                        ),
                        Column(
                            'gardening',
                            css_class='form-group col-md-6'
                        ),
                    ),
                    css_class='col-lg-6'
                ),
                css_class='row'
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
