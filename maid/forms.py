from decimal import Decimal
from typing import Any, Dict

from agency.models import Agency
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Field, Layout, Row, Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from employer_documentation.models import EmployerDoc
from onlinemaid.constants import TrueFalseChoices
from onlinemaid.helper_functions import encrypt_string, is_not_null, is_null
from onlinemaid.validators import validate_fin, validate_passport
from onlinemaid.widgets import OMCustomTextarea

from .constants import (CookingRemarksChoices, DisabledCareRemarksChoices,
                        ElderlyCareRemarksChoices,
                        GeneralHouseworkRemarksChoices,
                        InfantChildCareRemarksChoices, MaidAssessmentChoices,
                        MaidDietaryRestrictionChoices, MaidExperienceChoices,
                        MaidFoodPreferenceChoices,
                        MaidLanguageProficiencyChoices,
                        MaidPassportStatusChoices)
from .models import (Maid, MaidCooking, MaidDietaryRestriction,
                     MaidDisabledCare, MaidElderlyCare, MaidEmploymentHistory,
                     MaidFoodHandlingPreference, MaidGeneralHousework,
                     MaidInfantChildCare, MaidLanguageProficiency,
                     MaidLoanTransaction)
# from .widgets import CustomDateInput


class MaidForm(forms.ModelForm):
    class Meta:
        model = Maid
        exclude = [
            'agency', 'created_on', 'updated_on', 'about_me',
            'responsibilities', 'languages', 'passport_number_nonce',
            'passport_number_tag', 'fin_number_nonce', 'fin_number_tag'
        ]

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id')
        self.form_type = kwargs.pop('form_type')
        super().__init__(*args, **kwargs)
        self.FIELD_MAXLENGTH = 20
        self.initial.update({
            'passport_number': self.instance.get_passport_number(),
            'fin_number': self.instance.get_fin_number()
        })

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h5 class="fs-14">FDW Information</h5>'
                    ),
                    css_class='mb-3 mb-lg-4'
                ),
                css_class='row',
                css_id='fdwInformationGroup'
            ),
            Row(
                Column(
                    'photo',
                    css_class='form-group col-24'
                ),
                Column(
                    'status',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'expected_salary',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'expected_days_off',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'reference_number',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'name',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'country_of_origin',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'maid_type',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    Field(
                        'date_of_birth',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Date of birth'
                    ),
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'height',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'weight',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'marital_status',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'number_of_siblings',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'number_of_children',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'age_of_children',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'religion',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'place_of_birth',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'address_1',
                    css_class='form-group col-xl-12 pr-xl-3'
                ),
                Column(
                    'address_2',
                    css_class='form-group col-xl-12 pl-xl-3'
                ),
                Column(
                    'education_level',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'repatriation_airport',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'contact_number',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    'email',
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    'passport_status',
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    Field(
                        'passport_number',
                        maxlength=self.FIELD_MAXLENGTH,
                    ),
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    Field(
                        'passport_expiry',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Passport Expiry Date'
                    ),
                    css_class='form-group col-lg-12 pr-xl-3'
                ),
                Column(
                    Field(
                        'fin_number',
                        maxlength=self.FIELD_MAXLENGTH,
                    ),
                    css_class='form-group col-lg-12 pl-xl-3'
                ),
                Column(
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-xs-lg btn-primary w-xs-40 w-25 mx-2"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row'
            )
        )

    def clean_reference_number(self):
        reference_number = self.cleaned_data.get('reference_number')
        try:
            Maid.objects.get(
                agency=Agency.objects.get(
                    pk=self.agency_id
                ),
                reference_number=reference_number
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

        if is_not_null(cleaned_field):
            validate_passport("FDW", cleaned_field)
            # Encryption
            ciphertext, nonce, tag = encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY,
            )
            self.instance.passport_number_nonce = nonce
            self.instance.passport_number_tag = tag
            return ciphertext

    def clean_fin_number(self):
        cleaned_field = self.cleaned_data.get('fin_number')
        if cleaned_field:
            # If form errors then raise ValidationError, else continue
            validate_fin('FDW', cleaned_field)
            # Encryption
            ciphertext, nonce, tag = encrypt_string(
                cleaned_field,
                settings.ENCRYPTION_KEY,
            )
            self.instance.fin_number_nonce = nonce
            self.instance.fin_number_tag = tag
            return ciphertext

    def clean_expected_salary(self):
        field_name = 'expected_salary'
        cleaned_field = self.cleaned_data.get(field_name)
        if cleaned_field > 9999:
            self.add_error(
                field_name,
                ValidationError(
                    _('Invalid Value'),
                    code='invalid'
                )
            )
        return cleaned_field

    def clean_expected_days_off(self):
        field_name = 'expected_days_off'
        cleaned_field = self.cleaned_data.get(field_name)
        if cleaned_field > 4:
            self.add_error(
                field_name,
                ValidationError(
                    _('Invalid Value'),
                    code='invalid'
                )
            )
        return cleaned_field

    def clean_height(self):
        field_name = 'height'
        cleaned_field = self.cleaned_data.get(field_name)
        if cleaned_field > Decimal(200):
            self.add_error(
                field_name,
                ValidationError(
                    _('Invalid Value'),
                    code='invalid'
                )
            )
        return cleaned_field

    def clean_weight(self):
        field_name = 'weight'
        cleaned_field = self.cleaned_data.get(field_name)
        if cleaned_field > Decimal(100):
            self.add_error(
                field_name,
                ValidationError(
                    _('Invalid Value'),
                    code='invalid'
                )
            )
        return cleaned_field

    def clean_number_of_children(self):
        field_name = 'number_of_children'
        cleaned_field = self.cleaned_data.get(field_name)
        if cleaned_field > 20:
            self.add_error(
                field_name,
                ValidationError(
                    _('Invalid Value'),
                    code='invalid'
                )
            )
        return cleaned_field

    def clean_number_of_siblings(self):
        field_name = 'number_of_siblings'
        cleaned_field = self.cleaned_data.get(field_name)
        if cleaned_field > 20:
            self.add_error(
                field_name,
                ValidationError(
                    _('Invalid Value'),
                    code='invalid'
                )
            )
        return cleaned_field

    def clean_photo(self):
        photo = self.cleaned_data.get('photo', False)
        if photo:
            if photo.size > 4 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 4mb )")
            return photo
        else:
            raise ValidationError("Couldn't read uploaded image")

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        passport_number = cleaned_data.get('passport_number')
        passport_status = cleaned_data.get('passport_status')
        if(
            passport_status == MaidPassportStatusChoices.READY
            and is_null(passport_number)
        ):
            error_msg = _(
                'The maid \'s passport number cannot be empty if it is ready')
            raise ValidationError(error_msg)

        return cleaned_data

    def save(self, *args, **kwargs):
        self.instance.agency = Agency.objects.get(
            pk=self.agency_id
        )
        if self.changed_data:
            if (
                'name' in self.changed_data
                or 'passport_number' in self.changed_data
                or 'country_of_origin' in self.changed_data
            ):
                employer_doc_qs = EmployerDoc.objects.filter(
                    fdw=self.instance
                )
                for employer_doc in employer_doc_qs:
                    employer_doc.set_increment_version_number()
            elif 'email' in self.changed_data:
                self.instance.set_fdw_account_relation(
                    self.cleaned_data.get(
                        'email'
                    )
                )
        else:
            self.instance.set_fdw_account_relation(
                self.cleaned_data.get(
                    'email'
                )
            )
        return super().save(*args, **kwargs)


class MaidEmploymentHistoryForm(forms.ModelForm):
    class Meta:
        model = MaidEmploymentHistory
        exclude = ['maid']
        widgets = {
            'work_duties': OMCustomTextarea(attrs={
                'rows': '4',
                'cols': '100',
                'maxlength': '150'
            }),
            'reason_for_leaving': OMCustomTextarea(attrs={
                'rows': '4',
                'cols': '100',
                'maxlength': '100'
            })
        }

    def __init__(self, *args, **kwargs):
        self.maid_id = kwargs.pop('maid_id')
        self.maid = Maid.objects.get(
            pk=self.maid_id
        )
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, *args, **kwargs):
        self.instance.maid = self.maid
        return super().save(*args, **kwargs)


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
                        css_class="btn btn-xs-lg btn-primary w-50"
                    ),
                    css_class='form-group col-24 text-center'
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
                        css_class="btn btn-xs-lg btn-primary w-50"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row'
            )
        )


class MaidLoanTransactionForm(forms.ModelForm):
    class Meta:
        model = MaidLoanTransaction
        exclude = ['maid']
        widgets = {
            'remarks': OMCustomTextarea
        }

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
                            css_class='col-24 text-right'
                        )
                    ),
                    Row(
                        Column(
                            'date',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'description',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'amount',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'remarks',
                            css_class='form-group col-md-12 pl-xl-3'
                        )
                    )
                ),
                css_class='form-row'
            )
        )

    def save(self, *args, **kwargs):
        self.instance.maid = self.maid
        return super().save(*args, **kwargs)

# Generic Forms (forms.Form)


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
                        '<h4 class="fs-14">Spoken Language</h4>'
                    ),
                    css_class='mb-3 mb-lg-4'
                ),
                css_class='row',
                css_id='maidSpokenLanguageGroup'
            ),
            Row(
                Column(
                    'english',
                    css_class='form-group col-md-12 pr-xl-3'
                ),
                Column(
                    'malay',
                    css_class='form-group col-md-12 pl-xl-3'
                ),
                Column(
                    'mandarin',
                    css_class='form-group col-md-12 pr-xl-3'
                ),
                Column(
                    'chinese_dialect',
                    css_class='form-group col-md-12 pl-xl-3'
                ),
                Column(
                    'hindi',
                    css_class='form-group col-md-12 pr-xl-3'
                ),
                Column(
                    'tamil',
                    css_class='form-group col-md-12 pl-xl-3'
                ),
                css_class='form-row mb-xl-3'
            ),
            Div(
                Column(
                    HTML(
                        '''<h4 class="fs-14">Food Handling and Dietary
                        Restriction</h4>'''
                    ),
                    css_class='mb-3 mb-lg-4'
                ),
                css_class='row',
                css_id='maidFoodHandlingAndDietaryRestrictionGroup'
            ),
            Row(
                Column(
                    'food_handling_pork',
                    css_class='form-group col-md-12 pr-xl-3'
                ),
                Column(
                    'dietary_restriction_pork',
                    css_class='form-group col-md-12 pl-xl-3'
                ),
                Column(
                    'food_handling_beef',
                    css_class='form-group col-md-12 pr-xl-3'
                ),
                Column(
                    'dietary_restriction_beef',
                    css_class='form-group col-md-12 pl-xl-3'
                ),
                Column(
                    'dietary_restriction_veg',
                    css_class='form-group col-md-12 pr-xl-3'
                ),
                Column(
                    'food_handling_veg',
                    css_class='form-group col-md-12 pl-xl-3'
                ),
                css_class='form-row mb-xl-3'
            ),
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'dashboard_maid_information_update' maid_id %}"
                        class="btn btn-xs-lg btn-outline-primary w-xs-40 w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-xs-lg btn-primary w-xs-40 w-25 mx-2"
                    ),
                    css_class='form-group col-24 text-center'
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
            MaidFoodHandlingPreference.objects.create(
                maid=Maid.objects.get(pk=self.maid_id),
                preference=MaidFoodPreferenceChoices.PORK
            )

        if food_handling_beef == 'True':
            MaidFoodHandlingPreference.objects.create(
                maid=Maid.objects.get(pk=self.maid_id),
                preference=MaidFoodPreferenceChoices.BEEF
            )

        if food_handling_veg == 'True':
            MaidFoodHandlingPreference.objects.create(
                maid=Maid.objects.get(pk=self.maid_id),
                preference=MaidFoodPreferenceChoices.VEG
            )

        if dietary_restriction_pork == 'True':
            MaidDietaryRestriction.objects.create(
                maid=Maid.objects.get(pk=self.maid_id),
                restriction=MaidDietaryRestrictionChoices.PORK
            )

        if dietary_restriction_beef == 'True':
            MaidDietaryRestriction.objects.create(
                maid=Maid.objects.get(pk=self.maid_id),
                restriction=MaidDietaryRestrictionChoices.BEEF
            )

        if dietary_restriction_veg == 'True':
            MaidDietaryRestriction.objects.create(
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
        maid.set_languages()
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
        choices=TrueFalseChoices('Willing', 'Not willing')
    )

    cfi_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=MaidExperienceChoices.choices,
        initial=MaidExperienceChoices.NO
    )

    cfi_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=False,
        choices=InfantChildCareRemarksChoices.choices
    )

    cfi_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=OMCustomTextarea,
        required=False
    )

    cfe_assessment = forms.ChoiceField(
        label=_('Assessment'),
        required=True,
        choices=MaidAssessmentChoices.choices,
        initial=MaidAssessmentChoices.AVERAGE
    )

    cfe_willingness = forms.ChoiceField(
        label=_('Willingness'),
        required=True,
        choices=TrueFalseChoices('Willing', 'Not willing')
    )

    cfe_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=MaidExperienceChoices.choices,
        initial=MaidExperienceChoices.NO
    )

    cfe_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=ElderlyCareRemarksChoices.choices
    )

    cfe_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=OMCustomTextarea,
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
        choices=TrueFalseChoices('Willing', 'Not willing')
    )

    cfd_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=MaidExperienceChoices.choices,
        initial=MaidExperienceChoices.NO
    )

    cfd_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=DisabledCareRemarksChoices.choices
    )

    cfd_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=OMCustomTextarea,
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
        choices=TrueFalseChoices('Willing', 'Not willing')
    )

    geh_experience = forms.ChoiceField(
        label=_('Experience'),
        required=True,
        choices=MaidExperienceChoices.choices,
        initial=MaidExperienceChoices.NO
    )

    geh_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=GeneralHouseworkRemarksChoices.choices
    )

    geh_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=OMCustomTextarea,
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
        choices=TrueFalseChoices('Willing', 'Not willing')
    )

    cok_experience = forms.ChoiceField(
        label=_('Experience '),
        required=True,
        choices=MaidExperienceChoices.choices,
        initial=MaidExperienceChoices.NO
    )

    cok_remarks = forms.ChoiceField(
        label=_('Remarks'),
        required=True,
        choices=CookingRemarksChoices.choices
    )

    cok_other_remarks = forms.CharField(
        label=_('Other remarks'),
        widget=OMCustomTextarea,
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
                        '<h4 class="fs-14">Experience: Poor (1) ... Excellent(5)</h4>'
                    ),
                    css_class='mb-3 mb-lg-4'
                ),
                css_class='row',
                css_id='maidExperienceGroup'
            ),
            Div(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5 class="fs-14">Infant Child Care</h5>'
                            ),
                            css_class='col-24 mb-3 mb-lg-4'
                        ),
                        Column(
                            'cfi_assessment',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cfi_willingness',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cfi_experience',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cfi_remarks',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cfi_other_remarks',
                            css_class='form-group'
                        ),
                        css_class='form-row mb-xl-3'
                    ),
                    css_class='col-xl-24'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5 class="fs-14">Elderly Care</h5>'
                            ),
                            css_class='col-24 mb-3 mb-lg-4'
                        ),
                        Column(
                            'cfe_assessment',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cfe_willingness',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cfe_experience',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cfe_remarks',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cfe_other_remarks',
                            css_class='form-group'
                        ),
                        css_class='form-row mb-xl-3'
                    ),
                    css_class='col-xl-24'
                ),
                css_class='row'
            ),
            Div(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5 class="fs-14">Disabled Care</h5>'
                            ),
                            css_class='col-24 mb-3 mb-lg-4'
                        ),
                        Column(
                            'cfd_assessment',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cfd_willingness',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cfd_experience',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cfd_remarks',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cfd_other_remarks',
                            css_class='form-group'
                        ),
                        css_class='form-row mb-xl-3'
                    ),
                    css_class='col-xl-24'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5 class="fs-14">General Housework</h5>'
                            ),
                            css_class='col-24 mb-3 mb-lg-4'
                        ),
                        Column(
                            'geh_assessment',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'geh_willingness',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'geh_experience',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'geh_remarks',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'geh_other_remarks',
                            css_class='form-group'
                        ),
                        css_class='form-row mb-xl-3'
                    ),
                    css_class='col-xl-24'
                ),
                css_class='row'
            ),
            Div(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h5 class="fs-14">Cooking</h5>'
                            ),
                            css_class='col-24 mb-3 mb-lg-4'
                        ),
                        Column(
                            'cok_assessment',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cok_willingness',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cok_experience',
                            css_class='form-group col-md-12 pr-xl-3'
                        ),
                        Column(
                            'cok_remarks',
                            css_class='form-group col-md-12 pl-xl-3'
                        ),
                        Column(
                            'cok_other_remarks',
                            css_class='form-group'
                        ),
                        css_class='form-row mb-xl-3'
                    ),
                    css_class='col-xl-24'
                ),
                css_class='row'
            ),
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'dashboard_maid_languages_and_fhpdr_update' maid_id %}"
                        class="btn btn-xs-lg btn-outline-primary w-xs-40 w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-xs-lg btn-primary w-xs-40 w-25 mx-2"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row'
            )
        )

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data

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
        widget=OMCustomTextarea(attrs={
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
                        '<h4 class="fs-14">About FDW</h4>'
                    ),
                    css_class='mb-3 mb-lg-4'
                ),
                css_class='row',
                css_id='maidAboutMeGroup'
            ),
            Row(
                Column(
                    'about_me',
                    css_class='form-group col-24'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'dashboard_maid_employment_history_update' maid_id %}"
                        class="btn btn-xs-lg btn-outline-primary w-xs-40 w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Next',
                        css_class="btn btn-xs-lg btn-primary w-xs-40 w-25 mx-2"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row mb-xl-3'
            )
        )

    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        about_me = cleaned_data.get('about_me')
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        maid.about_me = about_me
        maid.save()
        return maid
