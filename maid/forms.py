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
from onlinemaid.helper_functions import validate_fin

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div, Field
from crispy_forms.bootstrap import PrependedText, AppendedText, InlineCheckboxes
from agency.models import Agency

# Imports from local apps
from .constants import (
    MaidLanguageChoices, MaidAssessmentChoices, MaidFoodPreferenceChoices, 
    MaidDietaryRestrictionChoices, MaidLanguageProficiencyChoices, InfantChildCareRemarksChoices,
    ElderlyCareRemarksChoices, DisabledCareRemarksChoices, CookingRemarksChoices,
    GeneralHouseworkRemarksChoices
)

from .models import (
    Maid, MaidLanguage, MaidInfantChildCare, MaidElderlyCare, MaidDisabledCare, 
    MaidGeneralHousework, MaidCooking, MaidFoodHandlingPreference, 
    MaidDietaryRestriction, MaidLoanTransaction,
    MaidFoodHandlingPreference, MaidDietaryRestriction,
    MaidEmploymentHistory, MaidLanguageProficiency
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
        input_formats=['%d %b %Y'],
        required=False
    )
    
    class Meta:
        model = Maid
        exclude = [
            'agency', 'created_on', 'updated_on', 'nonce', 'tag', 'about_me',
            'responsibilities', 'languages', 'skills_evaluation_method'
        ]

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id')
        self.form_type = kwargs.pop('form_type')
        super().__init__(*args, **kwargs)
        self.FIELD_MAXLENGTH = 20
        self.initial.update({'passport_number': self.instance.get_passport_number()})
                
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
                    Field(
                        'fin_number',
                        maxlength=self.FIELD_MAXLENGTH,
                    ),
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
            if self.form_type != 'update':
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

    def clean_fin_number(self):
        cleaned_field = self.cleaned_data.get('fin_number')

        # If form errors then raise ValidationError, else continue
        validate_fin(cleaned_field, self.FIELD_MAXLENGTH)

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

class MaidLanguagesAndFHPDRForm(forms.Form):
    english = forms.ChoiceField(
        label=_('English'),
        required=True,
        choices=MaidLanguageProficiencyChoices.choices
    )
    
    malay = forms.ChoiceField(
        label=_('Malay / Bahasa Indonesia'),
        required=True,
        choices=MaidLanguageProficiencyChoices.choices
    )
    
    mandarin = forms.ChoiceField(
        label=_('Mandarin'),
        required=True,
        choices=MaidLanguageProficiencyChoices.choices
    )
    
    chinese_dialect = forms.ChoiceField(
        label=_('Chinese Dialect'),
        required=True,
        choices=MaidLanguageProficiencyChoices.choices
    )
    
    hindi = forms.ChoiceField(
        label=_('Hindi'),
        required=True,
        choices=MaidLanguageProficiencyChoices.choices
    )
    
    tamil = forms.ChoiceField(
        label=_('Tamil'),
        required=True,
        choices=MaidLanguageProficiencyChoices.choices
    )
    
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
                        '<h4>Spoken Language</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidSpokenLanguageGroup'
            ),
            Row(
                Column(
                    'english',
                    css_class='col-md-6'
                ),
                Column(
                    'malay',
                    css_class='col-md-6'
                ),
                Column(
                    'mandarin',
                    css_class='col-md-6'
                ),
                Column(
                    'chinese_dialect',
                    css_class='col-md-6'
                ),
                Column(
                    'hindi',
                    css_class='col-md-6'
                ),
                Column(
                    'tamil',
                    css_class='col-md-6'
                ),
                css_class='form-group mb-xl-3'
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
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'dashboard_maid_information_update' maid_id %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-primary w-25 mx-2"
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
        maid.food_handling_preferences.all().delete()
        maid.dietary_restrictions.all().delete()
        food_handling_pork = cleaned_data.get('food_handling_pork')
        food_handling_beef = cleaned_data.get('food_handling_beef')
        food_handling_veg = cleaned_data.get('food_handling_veg')
        dietary_restriction_pork = cleaned_data.get('dietary_restriction_pork')
        dietary_restriction_beef = cleaned_data.get('dietary_restriction_beef')
        dietary_restriction_veg = cleaned_data.get('dietary_restriction_veg')
        if food_handling_pork == 'True':
            MaidFoodHandlingPreference.objects.get_or_create(
                maid=Maid.objects.get(pk=self.maid_id),
                preference=MaidFoodPreferenceChoices.PORK
            )
        if food_handling_beef == 'True':
            MaidFoodHandlingPreference.objects.get_or_create(
                maid=Maid.objects.get(pk=self.maid_id),
                preference=MaidFoodPreferenceChoices.BEEF
            )
        if food_handling_veg == 'True':
            MaidFoodHandlingPreference.objects.get_or_create(
                maid=Maid.objects.get(pk=self.maid_id),
                preference=MaidFoodPreferenceChoices.VEG
            )
        if dietary_restriction_pork == 'True':
            MaidDietaryRestriction.objects.get_or_create(
                maid=Maid.objects.get(pk=self.maid_id),
                restriction=MaidDietaryRestrictionChoices.PORK
            )
        if dietary_restriction_beef == 'True':
            MaidDietaryRestriction.objects.get_or_create(
                maid=Maid.objects.get(pk=self.maid_id),
                restriction=MaidDietaryRestrictionChoices.BEEF
            )
        if dietary_restriction_veg == 'True':
            MaidDietaryRestriction.objects.get_or_create(
                maid=Maid.objects.get(pk=self.maid_id),
                restriction=MaidDietaryRestrictionChoices.VEG
            )
        
        obj, created = MaidLanguageProficiency.objects.update_or_create(
            maid=Maid.objects.get(pk=self.maid_id),
            defaults={
                'english': cleaned_data.get('english'),
                'malay': cleaned_data.get('malay'),
                'mandarin': cleaned_data.get('mandarin'),
                'chinese_dialect': cleaned_data.get('chinese_dialect'),
                'hindi': cleaned_data.get('hindi'),
                'tamil': cleaned_data.get('tamil')
            }
        )
        return maid

class MaidExperienceForm(forms.Form):
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
        choices=InfantChildCareRemarksChoices.choices,
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
        choices=ElderlyCareRemarksChoices.choices
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
        choices=DisabledCareRemarksChoices.choices,
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
        choices=GeneralHouseworkRemarksChoices.choices
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
        label=_('Remarks'),
        required=True,
        choices=CookingRemarksChoices.choices
    )

    cok_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=forms.Textarea,
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
                    HTML(
                        '''
                        <a href="{% url 'dashboard_maid_languages_and_fhpdr_update' maid_id %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
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
        
        maid.skills_evaluation_method=skills_evaluation_method
        maid.save()
        
        MaidInfantChildCare.objects.update_or_create(
            maid=maid, 
            defaults={
                'assessment': cfi_assessment,
                'willingness': cfi_willingness,
                'experience': cfi_experience,
                'remarks': cfi_remarks,
                'other_remarks': cfi_other_remarks,
            }
        )
        
        MaidElderlyCare.objects.update_or_create(
            maid=maid, 
            defaults={
                'assessment': cfe_assessment,
                'willingness': cfe_willingness,
                'experience': cfe_experience,
                'remarks': cfe_remarks,
                'other_remarks': cfe_other_remarks,
            }
        )
        
        MaidDisabledCare.objects.update_or_create(
            maid=maid, 
            defaults={
                'assessment': cfd_assessment,
                'willingness': cfd_willingness,
                'experience': cfd_experience,
                'remarks': cfd_remarks,
                'other_remarks': cfd_other_remarks,
            }
        )
        
        MaidGeneralHousework.objects.update_or_create(
            maid=maid, 
            defaults={
                'assessment': geh_assessment,
                'willingness': geh_willingness,
                'experience': geh_experience,
                'remarks': geh_remarks,
                'other_remarks': geh_other_remarks,
            }
        )
        
        MaidCooking.objects.update_or_create(
            maid=maid, 
            defaults={
                'assessment': cok_assessment,
                'willingness': cok_willingness,
                'experience': cok_experience,
                'remarks': cok_remarks,
                'other_remarks': cok_other_remarks,
            }
        )

        return maid
        
class MaidAboutFDWForm(forms.Form):
    about_me = forms.CharField(
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
                        '<h4>About FDW</h4>'
                    ),
                ),
                css_class='row',
                css_id='maidAboutMeGroup'
            ),
            Row(
                Column(
                    'about_me',
                    css_class='col-12'
                ),
                css_class='form-group'
            ),
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'dashboard_maid_employment_history_update' maid_id %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
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
        about_me = cleaned_data.get('about_me')
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        maid.about_me=about_me
        maid.save()
        return maid

class MaidEmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = MaidEmploymentHistory
        exclude = ['maid']
        widgets = {
            'work_duties': forms.Textarea(attrs={
                'rows': '4',
                'cols': '100',
                'maxlength': '150'
            }),
            'reason_for_leaving': forms.Textarea(attrs={
                'rows': '4',
                'cols': '100',
                'maxlength': '100'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, *args, **kwargs):
        self.instance.maid = self.maid
        return super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.maid_id = kwargs.pop('maid_id')
        self.maid = Maid.objects.get(
            pk=self.maid_id
        )
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '''
                                <button class="btn btn-outline-primary">
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
                                    'start_date'
                                )
                            ),
                            Row(
                                Column(
                                    'end_date'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'work_duties'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'employer'
                                )
                            ),
                            Row(
                                Column(
                                    'country'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'reason_for_leaving'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class='form-group'
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

class MaidLoanTransactionForm(forms.ModelForm):
    class Meta:
        model = MaidLoanTransaction
        exclude = ['maid']

    def __init__(self, *args, **kwargs):
        self.maid_id = kwargs.pop('maid_id')
        self.maid = Maid.objects.get(
            pk=self.maid_id
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
                            'date',
                            css_class='col-md-6'
                        ),
                        Column(
                            'description',
                            css_class='col-md-6'
                        ),
                        Column(
                            'amount',
                            css_class='col-md-6'
                        ),
                        Column(
                            'remarks',
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class='form-group'
            )
        )

    def save(self, *args, **kwargs):
        self.instance.maid = self.maid
        return super().save(*args, **kwargs)
    
# Generic Forms (forms.Form)