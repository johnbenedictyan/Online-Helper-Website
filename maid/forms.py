# Python
import re

# Imports from django
from django import forms
from django.forms import formset_factory, inlineformset_factory, HiddenInput
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
    MaidEducationLevelChoices, MaidSkillsEvaluationMethod, 
    MaidLoanDescriptionChoices, MaidFoodPreferenceChoices, 
    MaidDietaryRestrictionChoices
)

from .models import (
    Maid, MaidLanguage, MaidInfantChildCare, MaidElderlyCare, MaidDisabledCare, 
    MaidGeneralHousework, MaidCooking, MaidFoodHandlingPreference, 
    MaidDietaryRestriction, MaidEmploymentHistory, MaidLoanTransaction,
    MaidFoodHandlingPreference, MaidDietaryRestriction
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
class MaidForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    passport_expiry = forms.DateField(
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    class Meta:
        model = Maid
        exclude = [
            'agency', 'created_on', 'updated_on', 'nonce', 'tag', 'remarks',
            'responsibilities', 'languages', 'skills_evaluation_method'
        ]

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id')
        self.form_type = kwargs.pop('form_type')
        super().__init__(*args, **kwargs)
        self.FIELD_MAXLENGTH = 20
        if self.form_type == 'update':
            if (
                self.instance.passport_number and 
                self.instance.passport_number!=b''
            ):
                try:
                    plaintext = decrypt_string(
                        self.instance.passport_number, 
                        settings.ENCRYPTION_KEY, 
                        self.instance.nonce, 
                        self.instance.tag
                    )
                    self.initial.update(
                        {
                            'passport_number': plaintext
                        }
                    )
                    
                except (ValueError, KeyError):
                    print("Incorrect decryption")
                    self.initial.update(
                        {
                            'passport_number': ''
                        }
                    )
                
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h5>FDW Information</h5>'
                    )
                ),
                css_class='row',
                css_id='fdwInformationGroup'
            ),
            Row(
                Column(
                    'photo',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'status',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'expected_salary',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'expected_days_off',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'reference_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'name',
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
                    'maid_type',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'date_of_birth',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'height',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'weight',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'marital_status',
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
                    'number_of_children',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'age_of_children',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'religion',
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
                    'education_level',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'repatriation_airport',
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
                    'passport_status',
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
                    'passport_expiry',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row form-group'
            ),
            Row(
                Column(
                    'about_me',
                    css_class='form-group col-12'
                ),
                css_class='form-row form-group'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
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
            msg = _('A maid with this reference number already exists')
            self.add_error('reference_number', msg)
        finally:
            return reference_number

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

    def save(self, *args, **kwargs):
        self.instance.agency = Agency.objects.get(
            pk=self.agency_id
        )
        return super().save(*args, **kwargs)
    
class MaidLanguageSpokenForm(forms.Form):
    language_spoken = forms.MultipleChoiceField(
        label=_('Language Spoken'),
        choices=MaidLanguageChoices.choices,
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        self.maid_id = kwargs.pop('maid_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h4>Language Spoken</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidLanguageSpokenGroup'
            ),
            Row(
                Column(
                    Field(
                        'language_spoken',
                        template='widgets/custom-inline-checkbox.html'
                    ),
                    css_class='form-group'
                ),
                css_class='mb-xl-3'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )
        
    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        
        maid.languages.clear()
        for language in cleaned_data.get('language_spoken'):
            maid.languages.add(
                MaidLanguage.objects.get(
                    language=language
                )
            )
            
        return maid

class MaidFoodHandlingPreferencesDietaryRestrictionsForm(forms.Form):
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

    def __init__(self, *args, **kwargs):
        self.maid_id = kwargs.pop('maid_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h4>Food Handling and Dietary Restriction</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidFoodHandlingAndDietaryRestrictionGroup'
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
                css_class='form-group mb-xl-3'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )
    
    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        maid.food_handling_preferences.clear()
        maid.dietary_restrictions.clear()
        food_handling_pork = cleaned_data.get('food_handling_pork')
        food_handling_beef = cleaned_data.get('food_handling_beef')
        food_handling_veg = cleaned_data.get('food_handling_veg')
        dietary_restriction_pork = cleaned_data.get('dietary_restriction_pork')
        dietary_restriction_beef = cleaned_data.get('dietary_restriction_beef')
        dietary_restriction_veg = cleaned_data.get('dietary_restriction_veg')
        if food_handling_pork == 'True':
            MaidFoodHandlingPreference.objects.get_or_create(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.PORK
            )
        if food_handling_beef == 'True':
            MaidFoodHandlingPreference.objects.get_or_create(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.BEEF
            )
        if food_handling_veg == 'True':
            MaidFoodHandlingPreference.objects.get_or_create(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.VEG
            )
        if dietary_restriction_pork == 'True':
            MaidDietaryRestriction.objects.get_or_create(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.PORK
            )
        if dietary_restriction_beef == 'True':
            MaidDietaryRestriction.objects.get_or_create(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.BEEF
            )
        if dietary_restriction_veg == 'True':
            MaidDietaryRestriction.objects.get_or_create(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.VEG
            )
            
        return maid

class MaidExperienceForm(forms.Form):
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
    
    # care_for_pets = forms.ChoiceField(
    #     label=_('Care for pets'),
    #     required=True,
    #     choices=TrueFalseChoices('Able', 'Unable')
    # )
    
    # gardening = forms.ChoiceField(
    #     label=_('Gardening'),
    #     required=True,
    #     choices=TrueFalseChoices('Able', 'Unable')
    # )

    def __init__(self, *args, **kwargs):
        self.maid_id = kwargs.pop('maid_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h4>Experience: Poor (1) ... Excellent(5)</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidExperienceGroup'
            ),
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
                css_class='row'
            ),
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

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        skills_evaluation_method = cleaned_data.get('skills_evaluation_method')
        
        cfi_assessment = cleaned_data.get('cfi_assessment')
        cfi_willingness = cleaned_data.get('cfi_willingness')
        cfi_experience = cleaned_data.get('cfi_experience')
        cfi_remarks = cleaned_data.get('cfi_remarks')
        cfi_other_remarks = cleaned_data.get('cfi_other_remarks')

        cfe_assessment = cleaned_data.get('cfe_assessment')
        cfe_willingness = cleaned_data.get('cfe_willingness')
        cfe_experience = cleaned_data.get('cfe_experience')
        cfe_remarks = cleaned_data.get('cfe_remarks')
        cfe_other_remarks = cleaned_data.get('cfe_other_remarks')
        
        cfd_assessment = cleaned_data.get('cfd_assessment')
        cfd_willingness = cleaned_data.get('cfd_willingness')
        cfd_experience = cleaned_data.get('cfd_experience')
        cfd_remarks = cleaned_data.get('cfd_remarks')
        cfd_other_remarks = cleaned_data.get('cfd_other_remarks')

        geh_assessment = cleaned_data.get('geh_assessment')
        geh_willingness = cleaned_data.get('geh_willingness')
        geh_experience = cleaned_data.get('geh_experience')
        geh_remarks = cleaned_data.get('geh_remarks')
        geh_other_remarks = cleaned_data.get('geh_other_remarks')

        cok_assessment = cleaned_data.get('cok_assessment')
        cok_willingness = cleaned_data.get('cok_willingness')
        cok_experience = cleaned_data.get('cok_experience')
        cok_remarks = cleaned_data.get('cok_remarks')
        cok_other_remarks = cleaned_data.get('cok_other_remarks')
        
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        
        maid.update(skills_evaluation_method=skills_evaluation_method)
        
        MaidInfantChildCare.objects.update_or_create(
            maid__pk=self.maid_id, 
            defaults={
                'assessment': cfi_assessment,
                'willingness': cfi_willingness,
                'experience': cfi_experience,
                'remarks': cfi_remarks,
                'other_remarks': cfi_other_remarks,
            }
        )
        
        MaidElderlyCare.objects.update_or_create(
            maid__pk=self.maid_id, 
            defaults={
                'assessment': cfe_assessment,
                'willingness': cfe_willingness,
                'experience': cfe_experience,
                'remarks': cfe_remarks,
                'other_remarks': cfe_other_remarks,
            }
        )
        
        MaidDisabledCare.objects.update_or_create(
            maid__pk=self.maid_id, 
            defaults={
                'assessment': cfd_assessment,
                'willingness': cfd_willingness,
                'experience': cfd_experience,
                'remarks': cfd_remarks,
                'other_remarks': cfd_other_remarks,
            }
        )
        
        MaidGeneralHousework.objects.update_or_create(
            maid__pk=self.maid_id, 
            defaults={
                'assessment': geh_assessment,
                'willingness': geh_willingness,
                'experience': geh_experience,
                'remarks': geh_remarks,
                'other_remarks': geh_other_remarks,
            }
        )
        
        MaidCooking.objects.update_or_create(
            maid__pk=self.maid_id, 
            defaults={
                'assessment': cok_assessment,
                'willingness': cok_willingness,
                'experience': cok_experience,
                'remarks': cok_remarks,
                'other_remarks': cok_other_remarks,
            }
        )

        return maid
        
class MaidOtherRemarksForm(forms.Form):
    remarks = forms.CharField(
        label=_(''),
        widget=forms.Textarea(attrs={
            'rows': '10',
            'cols': '100',
            'maxlength': '300'    
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.maid_id = kwargs.pop('maid_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h4>Other Remarks</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidOtherRemarksGroup'
            ),
            Row(
                Column(
                    'remarks',
                    css_class='col-12'
                ),
                css_class='form-group'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        remarks = cleaned_data.get('remarks')
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        maid.update(remarks=remarks)
        return maid

# class MaidUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Maid
#         exclude = ['agency', 'created_on', 'updated_on', 'agency_fee_amount',
#             'responsibilities', 'nonce', 'tag'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.FIELD_MAXLENGTH = 20

#         ###################################################################################################### TO BE REMOVED
#         '''
#         Decryption
#         '''
#         if self.instance.passport_number and self.instance.passport_number!=b'':
#             try:
#                 plaintext = decrypt_string(self.instance.passport_number, settings.ENCRYPTION_KEY, self.instance.nonce, self.instance.tag)
#                 self.initial.update({'passport_number': plaintext})
#             except (ValueError, KeyError):
#                 print("Incorrect decryption")
#                 self.initial.update({'passport_number': ''})
#         ###################################################################################################### TO BE REMOVED

#         #  Remove passport number from initial form display
#         # self.initial.update({'passport_number':''})
        
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Row(
#                 Column(
#                     'reference_number',
#                     css_class='form-group col-md-6'
#                 ),
#                 Column(
#                     'maid_type',
#                     css_class='form-group col-md-6'
#                 ),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column(
#                     Field(
#                         'passport_number',
#                         maxlength=self.FIELD_MAXLENGTH,
#                     ),
#                     css_class='form-group col-md-6'
#                 ),
#                 Column(
#                     'photo',
#                     css_class='form-group col-md-6'
#                 ),
#                 css_class='form-row form-group'
#             ),
#             Row(
#                 Column(
#                     PrependedText(
#                         'salary', '$'
#                     ),
#                     css_class='form-group col-md-6'
#                 ),
#                 Column(
#                     PrependedText(
#                         'personal_loan_amount', '$'
#                     ),
#                     css_class='form-group col-md-6'
#                 ),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column(
#                     'days_off',
#                     css_class='form-group col-md-4'
#                 ),
#                 Column(
#                     'passport_status',
#                     css_class='form-group col-md-4'
#                 ),
#                 Column(
#                     'repatriation_airport',
#                     css_class='form-group col-md-4'
#                 ),
#                 css_class='form-row'
#             ),
#             Row(
#                 Column(
#                     'remarks',
#                     css_class='form-group col'
#                 ),
#                 css_class='form-row'
#             ),
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
 
#     def clean_reference_number(self):
#         reference_number = self.cleaned_data.get('reference_number')
#         try:
#             maid = Maid.objects.get(
#                 agency = Agency.objects.get(
#                     pk = self.instance.agency.pk
#                 ),
#                 reference_number = reference_number
#             )
#         except Maid.DoesNotExist:
#             return reference_number
#         else:
#             if maid.pk==self.instance.pk:
#                 return reference_number
#             else:
#                 msg = _('A maid with this reference number already exists')
#                 self.add_error('reference_number', msg)
       
#     def clean_passport_number(self):
#         cleaned_field = self.cleaned_data.get('passport_number')

#         # If form errors then raise ValidationError, else continue
#         validate_passport_number(cleaned_field, self.FIELD_MAXLENGTH)

#         # Encryption
#         ciphertext, self.instance.nonce, self.instance.tag = encrypt_string(
#             cleaned_field,
#             settings.ENCRYPTION_KEY
#         )

#         return ciphertext

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

# MaidEmploymentHistoryFormSet = inlineformset_factory(
#     parent_model = Maid,
#     model = MaidEmploymentHistory,
#     fields = ['country','start_date','end_date','work_duties',]
# )

# class MaidEmploymentHistoryFormSetHelper(FormHelper):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.form_method = 'post'
#         self.layout = Layout(
#             HTML('''
#                 <h5>Past employment {{ forloop.counter }}</h5>
#             '''),
#             Row(
#                 Column(
#                     Row(
#                         Column(
#                             'country',
#                             css_class='form-group col-12'
#                         ),
#                         Column(
#                             Field(
#                                 'start_date',
#                                 type='text',
#                                 onfocus="(this.type='date')",
#                                 placeholder='Past employment start date'
#                             ),
#                             css_class='form-group col-12'
#                         ),
#                         Column(
#                             Field(
#                                 'end_date',
#                                 type='text',
#                                 onfocus="(this.type='date')",
#                                 placeholder='Past employment end date'
#                             ),
#                             css_class='form-group col-12'
#                         ),
#                     ),
#                     css_class='form-group col-md-6'
#                 ),
#                 Column(
#                     InlineCheckboxes('work_duties'),
#                     css_class='form-group col-md-6 work-duties'
#                 ),
#                 css_class='form-row'
#             ),
#             HTML('<hr>'),
#         )
#         self.render_required_fields = True

class MaidLoanTransactionForm(forms.ModelForm):
    class Meta:
        model = MaidLoanTransaction
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
class MainMaidCreationForm(forms.ModelForm):
    # Maid Information
    country_of_origin = forms.ChoiceField(
        label=_('Country of Origin'),
        choices=MaidCountryOfOrigin.choices,
        required=True
    )

    salary = forms.DecimalField(
        label=_('Expected Salary'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=True,
        initial=0
    )

    contact_number = forms.CharField(
        label=_('Contact Number'),
        max_length=30,
        required=True
    )
    
    # Maid Personal Details
    date_of_birth = forms.DateField(
        label=_('Date of Birth'),
        required=True,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
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

    marital_status = forms.ChoiceField(
        label='Marital Status',
        required=True,
        choices=MaritalStatusChoices.choices,
        initial=MaritalStatusChoices.SINGLE
    )
    
    number_of_siblings = forms.IntegerField(
        label='Number of Siblings',
        required=True,
        initial=0,
        max_value=20,
        min_value=0
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
    
    religion = forms.ChoiceField(
        label=_('Religion'),
        choices=MaidReligionChoices.choices,
        initial=MaidReligionChoices.NONE,
        required=True
    )
    
    place_of_birth = forms.CharField(
        label='Place of Birth',
        max_length=25,
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

    education_level = forms.ChoiceField(
        label=_('Education Level'),
        required=True,
        choices=MaidEducationLevelChoices.choices,
        initial=MaidEducationLevelChoices.HIGH_SCHOOL
    )
    
    repatriation_airport = forms.CharField(
        label='Repatriation Airport',
        max_length=100,
        required=True
    )

    # Language Spoken
    language_spoken = forms.MultipleChoiceField(
        label=_('Language Spoken'),
        choices=MaidLanguageChoices.choices,
        widget=forms.CheckboxSelectMultiple(),
        required=True
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
    
    # Employment History
    employment_history_start_date_1 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_1 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_1 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_1 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_1 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )
    
    employment_history_reason_for_leaving_1 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_2 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_2 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_2 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_2 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_2 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )
    
    employment_history_reason_for_leaving_2 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_3 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_3 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_3 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_3 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_3 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )
    
    employment_history_reason_for_leaving_3 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_4 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_4 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_4 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_4 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_4 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )
    
    employment_history_reason_for_leaving_4 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_5 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_5 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_5 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_5 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_5 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )

    employment_history_reason_for_leaving_5 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_6 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_6 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_6 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_6 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_6 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )
    
    employment_history_reason_for_leaving_6 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_7 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_7 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_7 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_7 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_7 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )

    employment_history_reason_for_leaving_7 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_8 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_8 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_8 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_8 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_8 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )
    
    employment_history_reason_for_leaving_8 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_9 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_9 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_9 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_9 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_9 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )
    
    employment_history_reason_for_leaving_9 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )

    employment_history_start_date_10 = forms.DateField(
        label=_('Start Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_end_date_10 = forms.DateField(
        label=_('End Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    employment_history_employer_10 = forms.CharField(
        label=_('Country or Race of Employer'),
        required=False
    )
    
    employment_history_country_10 = forms.CharField(
        label=_('Country'),
        required=False
    )

    employment_history_work_duties_10 = forms.CharField(
        label=_('Work Duties'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '150'    
        })
    )

    employment_history_reason_for_leaving_10 = forms.CharField(
        label=_('Reason for Leaving'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '4',
            'cols': '100',
            'maxlength': '100'    
        })
    )
    
    # Maid Loan
    maid_loan_hash_1 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    maid_loan_date_1 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_1 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_1 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_1 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_2 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    maid_loan_date_2 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_2 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_2 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_2 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_3 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_3 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_3 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_3 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_3 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_4 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_4 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_4 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_4 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_4 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_5 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_5 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_5 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_5 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_5 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_6 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_6 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_6 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_6 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_6 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_7 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_7 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_7 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_7 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_7 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_8 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_8 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_8 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_8 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_8 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_9 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_9 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_9 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_9 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_9 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_10 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_10 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_10 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_10 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_10 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_11 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_11 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_11 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_11 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_11 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_12 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_12 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_12 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_12 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_12 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_13 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_13 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_13 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_13 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_13 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_14 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_14 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_14 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_14 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_14 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_15 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_15 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_15 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_15 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_15 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_16 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_16 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_16 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_16 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_16 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_17 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_17 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_17 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_17 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_17 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_18 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_18 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_18 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_18 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_18 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_19 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_19 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_19 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_19 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_19 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    maid_loan_hash_20 = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    maid_loan_date_20 = forms.DateField(
        label=_('Date'),
        required=False,
        widget=CustomDateInput(),
        input_formats=['%d %b %Y']
    )
    
    maid_loan_description_20 = forms.ChoiceField(
        choices=MaidLoanDescriptionChoices.choices,
        label=_('Description'),
        required=False
    )
    
    maid_loan_amount_20 = forms.DecimalField(
        label=_('Amount'),
        max_digits=7,
        decimal_places=2,
        max_value=10000,
        min_value=0,
        required=False,
        initial=0
    )
    
    maid_loan_remarks_20 = forms.CharField(
        label=_('Remarks'),
        max_length=80,
        required=False
    )
    
    # Remarks
    remarks = forms.CharField(
        label=_(''),
        widget=forms.Textarea(attrs={
            'rows': '10',
            'cols': '100',
            'maxlength': '300'    
        }),
        required=False
    )
    
    # Override Field for the checking of duplicate fdws
    override = forms.BooleanField(
        widget=forms.HiddenInput(),
        initial=False
    )

    class Meta:
        model = Maid
        fields = [
            'reference_number', 'name', 'passport_number', 'photo', 'maid_type',
            'expected_days_off', 'passport_status', 'skills_evaluation_method'
        ]

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id')
        self.update = kwargs.pop('update')
        super().__init__(*args, **kwargs)
        self.fields['passport_number'].required = False
        eh_display_map = {
            'eh_1_display': '',
            'eh_2_display': 'd-none',
            'eh_3_display': 'd-none',
            'eh_4_display': 'd-none',
            'eh_5_display': 'd-none',
            'eh_6_display': 'd-none',
            'eh_7_display': 'd-none',
            'eh_8_display': 'd-none',
            'eh_9_display': 'd-none',
            'eh_10_display': 'd-none',
        }
        ml_display_map = {
            'ml_1_display': '',
            'ml_2_display': 'd-none',
            'ml_3_display': 'd-none',
            'ml_4_display': 'd-none',
            'ml_5_display': 'd-none',
            'ml_6_display': 'd-none',
            'ml_7_display': 'd-none',
            'ml_8_display': 'd-none',
            'ml_9_display': 'd-none',
            'ml_10_display': 'd-none',
            'ml_11_display': 'd-none',
            'ml_12_display': 'd-none',
            'ml_13_display': 'd-none',
            'ml_14_display': 'd-none',
            'ml_15_display': 'd-none',
            'ml_16_display': 'd-none',
            'ml_17_display': 'd-none',
            'ml_18_display': 'd-none',
            'ml_19_display': 'd-none',
            'ml_20_display': 'd-none',
        }
        maidLoanRowNumber = maidEmploymentHistoryRowNumber = 1
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h4>Maid Photo</h4>'
                    )
                ),
                css_class='row',
                css_id='maidPhotoGroup'
            ),
            Row(
                Column(
                    HTML(
                        "<img src='{{ MEDIA_URL }}{% if form.photo.value%}{{form.photo.value}}{% else %}/thumbnails/default{% endif %}' alt='' class='img-fluid thumbnail' >"
                    ),
                    'photo',
                    css_class='form-group col-md-6'
                )
            ),
            Div(
                Column(
                    HTML(
                        '<h4>Maid Information</h4>'
                    )
                ),
                css_class='row',
                css_id='maidInformationGroup'
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
                    'salary',
                    css_class='col-md-6'
                ),
                Column(
                    'expected_days_off',
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
                css_class='row form-group mb-xl-3'
            ),
            Div(
                Column(
                    HTML(
                        '<h4>Personal Details</h4>'
                    )
                ),
                css_class='row',
                css_id='maidPersonalDetailsGroup'
            ),
            Div(
                Column(
                    'date_of_birth',
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
                    'education_level',
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
                css_class='row form-group mb-xl-3'
            ),
            Div(
                Column(
                    HTML(
                        '<h4>Language Spoken</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidLanguageSpokenGroup'
            ),
            Row(
                Column(
                    Field(
                        'language_spoken',
                        template='widgets/custom-inline-checkbox.html'
                    ),
                    css_class='form-group'
                ),
                css_class='mb-xl-3'
            ),
            Div(
                Column(
                    HTML(
                        '<h4>Food Handling and Dietary Restriction</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidFoodHandlingAndDietaryRestrictionGroup'
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
                css_class='form-group mb-xl-3'
            ),
            Div(
                Column(
                    HTML(
                        '<h4>Experience</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidExperienceGroup'
            ),
            Row(
                Column(
                    'skills_evaluation_method',
                    css_class='form-group col-12'
                )
            ),
            Row(
                Column(
                    HTML(
                        '<h6>Infant Child Care</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    'cfi_willingness',
                    css_class='col-md-6'
                ),
                Column(
                    'cfi_assessment',
                    css_class='col-md-6'
                ),
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
            Row(
                Column(
                    HTML(
                        '<h6>Elderly Care</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    'cfe_willingness',
                    css_class='col-md-6'
                ),
                Column(
                    'cfe_assessment',
                    css_class='col-md-6'
                ),
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
            Row(
                Column(
                    HTML(
                        '<h6>Disabled Care</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    'cfd_willingness',
                    css_class='col-md-6'
                ),
                Column(
                    'cfd_assessment',
                    css_class='col-md-6'
                ),
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
            Row(
                Column(
                    HTML(
                        '<h6>General Housework</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    'geh_willingness',
                    css_class='col-md-6'
                ),
                Column(
                    'geh_assessment',
                    css_class='col-md-6'
                ),
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
            Row(
                Column(
                    HTML(
                        '<h6>Cooking</h6>'
                    ),
                    css_class='col-12'
                ),
                Column(
                    'cok_willingness',
                    css_class='col-md-6'
                ),
                Column(
                    'cok_assessment',
                    css_class='col-md-6'
                ),
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
            Div(
                Column(
                    HTML(
                        '<h4>Employment History</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidEmploymentHistoryGroup'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="1"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_1'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_1'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_1'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_1'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_1'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_1'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_1_display"]} form-group',
                css_id='eh_entry_section_1'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="2"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_2'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_2'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_2'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_2'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_2'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_2'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_2_display"]} form-group',
                css_id='eh_entry_section_2'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="3"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_3'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_3'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_3'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_3'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_3'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_3'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_3_display"]} form-group',
                css_id='eh_entry_section_3'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="4"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_4'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_4'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_4'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_4'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_4'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_4'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_4_display"]} form-group',
                css_id='eh_entry_section_4'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="5"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_5'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_5'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_5'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_5'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_5'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_5'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_5_display"]} form-group',
                css_id='eh_entry_section_5'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="6"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_6'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_6'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_6'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_6'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_6'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_6'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_6_display"]} form-group',
                css_id='eh_entry_section_6'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="7"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_7'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_7'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_7'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_7'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_7'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_7'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_7_display"]} form-group',
                css_id='eh_entry_section_7'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="8"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_8'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_8'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_8'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_8'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_8'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_8'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_8_display"]} form-group',
                css_id='eh_entry_section_8'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="9"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_9'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_9'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_9'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_9'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_9'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_9'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_9_display"]} form-group',
                css_id='eh_entry_section_9'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="10"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_start_date_10'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_end_date_10'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_work_duties_10'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employment_history_employer_10'
                                )
                            ),
                            Row(
                                Column(
                                    'employment_history_country_10'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'employment_history_reason_for_leaving_10'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class=f'{eh_display_map["eh_10_display"]} form-group',
                css_id='eh_entry_section_10'
            ),
            Div(
                Column(
                    HTML(
                        f'''
                        <a class="btn btn-primary"
                        id="maidEmploymentHistoryAdditionButton" 
                        data-rowNumber="{maidEmploymentHistoryRowNumber}">
                        Add new entry
                        </a>'''
                    ),
                    css_class='col-12 text-right mb-xl-3'
                )
            ),
            Div(
                Column(
                    HTML(
                        '<h4>Maid Loan</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidLoanGroup'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="1"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_1',
                Column(
                    'maid_loan_date_1',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_1',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_1',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_1',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_1_display"]} row form-group',
                css_id='ml_entry_section_1'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="2"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_2',
                Column(
                    'maid_loan_date_2',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_2',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_2',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_2',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_2_display"]} row form-group',
                css_id='ml_entry_section_2'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="3"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_3',
                Column(
                    'maid_loan_date_3',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_3',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_3',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_3',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_3_display"]} row form-group',
                css_id='ml_entry_section_3'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="4"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_4',
                Column(
                    'maid_loan_date_4',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_4',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_4',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_4',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_4_display"]} row form-group',
                css_id='ml_entry_section_4'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="5"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_5',
                Column(
                    'maid_loan_date_5',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_5',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_5',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_5',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_5_display"]} row form-group',
                css_id='ml_entry_section_5'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="6"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_6',
                Column(
                    'maid_loan_date_6',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_6',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_6',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_6',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_6_display"]} row form-group',
                css_id='ml_entry_section_6'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="7"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_7',
                Column(
                    'maid_loan_date_7',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_7',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_7',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_7',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_7_display"]} row form-group',
                css_id='ml_entry_section_7'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="8"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_8',
                Column(
                    'maid_loan_date_8',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_8',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_8',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_8',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_8_display"]} row form-group',
                css_id='ml_entry_section_8'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="9"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_9',
                Column(
                    'maid_loan_date_9',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_9',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_9',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_9',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_9_display"]} row form-group',
                css_id='ml_entry_section_9'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="10"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_10',
                Column(
                    'maid_loan_date_10',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_10',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_10',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_10',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_10_display"]} row form-group',
                css_id='ml_entry_section_10'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="11"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_11',
                Column(
                    'maid_loan_date_11',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_11',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_11',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_11',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_11_display"]} row form-group',
                css_id='ml_entry_section_11'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="12"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_12',
                Column(
                    'maid_loan_date_12',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_12',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_12',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_12',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_12_display"]} row form-group',
                css_id='ml_entry_section_12'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="13"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_13',
                Column(
                    'maid_loan_date_13',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_13',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_13',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_13',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_13_display"]} row form-group',
                css_id='ml_entry_section_13'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="14"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_14',
                Column(
                    'maid_loan_date_14',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_14',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_14',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_14',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_14_display"]} row form-group',
                css_id='ml_entry_section_14'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="15"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_15',
                Column(
                    'maid_loan_date_15',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_15',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_15',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_15',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_15_display"]} row form-group',
                css_id='ml_entry_section_15'
            ),
            Div(
                Column(
                        HTML(
                            '''
                            <button class="btn btn-outline-primary 
                                            ml-delete-button"
                                    data-rowNumber="16"
                            >
                                <i class="fas fa-times"></i>
                            </button>'''
                        ),
                        css_class='col-12 text-right'
                ),
                'maid_loan_hash_16',
                Column(
                    'maid_loan_date_16',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_16',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_16',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_16',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_16_display"]} row form-group',
                css_id='ml_entry_section_16'
            ),
            Div(
                Column(
                    HTML(
                        '''
                        <button class="btn btn-outline-primary 
                                        ml-delete-button"
                                data-rowNumber="17"
                        >
                            <i class="fas fa-times"></i>
                        </button>'''
                    ),
                    css_class='col-12 text-right'
                ),
                'maid_loan_hash_17',
                Column(
                    'maid_loan_date_17',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_17',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_17',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_17',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_17_display"]} row form-group',
                css_id='ml_entry_section_17'
            ),
            Div(
                Column(
                    HTML(
                        '''
                        <button class="btn btn-outline-primary 
                                        ml-delete-button"
                                data-rowNumber="18"
                        >
                            <i class="fas fa-times"></i>
                        </button>'''
                    ),
                    css_class='col-12 text-right'
                ),
                'maid_loan_hash_18',
                Column(
                    'maid_loan_date_18',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_18',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_18',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_18',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_18_display"]} row form-group',
                css_id='ml_entry_section_18'
            ),
            Div(
                Column(
                    HTML(
                        '''
                        <button class="btn btn-outline-primary 
                                        ml-delete-button"
                                data-rowNumber="19"
                        >
                            <i class="fas fa-times"></i>
                        </button>'''
                    ),
                    css_class='col-12 text-right'
                ),
                'maid_loan_hash_19',
                Column(
                    'maid_loan_date_19',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_19',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_19',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_19',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_19_display"]} row form-group',
                css_id='ml_entry_section_19'
            ),
            Div(
                Column(
                    HTML(
                        '''
                        <button class="btn btn-outline-primary 
                                        ml-delete-button"
                                data-rowNumber="20"
                        >
                            <i class="fas fa-times"></i>
                        </button>'''
                    ),
                    css_class='col-12 text-right'
                ),
                'maid_loan_hash_20',
                Column(
                    'maid_loan_date_20',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_description_20',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_amount_20',
                    css_class='col-md-6'
                ),
                Column(
                    'maid_loan_remarks_20',
                    css_class='col-md-6'
                ),
                css_class=f'{ml_display_map["ml_20_display"]} row form-group',
                css_id='ml_entry_section_20'
            ),
            Div(
                Column(
                    HTML(
                        f'''
                        <a class="btn btn-primary"
                        id="maidLoanAdditionButton" 
                        data-rowNumber="{maidLoanRowNumber}">
                        Add new entry
                        </a>'''
                    ),
                    css_class='col-12 text-right mb-xl-3'
                )
            ),
            Div(
                Column(
                    HTML(
                        '<h4>Other Remarks</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidOtherRemarksGroup'
            ),
            Row(
                Column(
                    'remarks',
                    css_class='col-12'
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
        passport_status = self.cleaned_data.get('passport_status')
        print(self.cleaned_data.get('passport_status'))
        if passport_status == 1 and passport_number == b'':
            self.add_error(
                'passport_number',
                ValidationError(_('This field is required'), code='required')
            )
        else:
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
        date_of_birth = cleaned_data.get('date_of_birth')
        country_of_origin = cleaned_data.get('country_of_origin')
        place_of_birth = cleaned_data.get('place_of_birth')
        override = cleaned_data.get('override')
        possible_duplicate_maids = Maid.objects.filter(
            agency__pk=self.agency_id,
            name__trigram_similar = name,
            date_of_birth = date_of_birth,
            country_of_origin = country_of_origin,
            place_of_birth__trigram_similar = place_of_birth
        )
        # This value 3 should be a threshold settings

        pdm_count = possible_duplicate_maids.count()
        if pdm_count > 0 and pdm_count < 3 and override != True:
            msg = "This FDW looks similar to these other fdws: "
            for i in possible_duplicate_maids:
                msg += f"""
                    <a href="{reverse_lazy('maid_update', pk=i.pk)}" 
                    target="_blank">
                    {i.name}
                    </a>
                """
            self.data = self.data.copy()
            self.data['override'] = True
            self.add_error(None, msg)

        return cleaned_data
    
    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data

        # Encrypting the passport number
        raw_passport_number = cleaned_data.get('passport_number')
        encrypted_passport_number, nonce, tag = encrypt_string(
            raw_passport_number,
            settings.ENCRYPTION_KEY
        )

        self.agency = Agency.objects.get(
            pk=self.agency_id
        )
        self.passport_number = encrypted_passport_number
        self.nonce = nonce
        self.tag = tag
        new_maid = super().save(*args, **kwargs)
        
        for language in cleaned_data.get('language_spoken'):
            new_maid_personal_details.languages.add(
                MaidLanguage.objects.get(
                    language=language
                )
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
        MaidLoanTransaction.objects.create(
            maid=new_maid,
            amount=cleaned_data.get('initial_agency_fee_amount'),
            transaction_type='ADD',
            description=cleaned_data.get('initial_agency_fee_description'),
            transaction_date=cleaned_data.get('transaction_date')
        )
        return new_maid
