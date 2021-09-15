# Django Imports
from django import forms

# Foreign Apps Imports
# from captcha.fields import ReCaptchaField
# from captcha.widgets import ReCaptchaV3
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit, Row, Column, Field

# Project Apps Imports
from maid.models import MaidResponsibility, MaidLanguage
from onlinemaid.widgets import OMCustomTextarea

# App Imports
from .constants import MAID_TYPE_CHOICES, MAID_NATIONALITY_CHOICES
from .fields import MaidResponsibilityChoiceField
from .models import GeneralEnquiry, ShortlistedEnquiry

# Start of Forms

# Model Forms


class GeneralEnquiryForm(forms.ModelForm):
    maid_nationality = forms.MultipleChoiceField(
        label='',
        choices=MAID_NATIONALITY_CHOICES,
        widget=forms.CheckboxSelectMultiple()
    )

    maid_type = forms.MultipleChoiceField(
        label='',
        choices=MAID_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple()
    )

    maid_responsibility = MaidResponsibilityChoiceField(
        label='',
        queryset=MaidResponsibility.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    languages_spoken = forms.ModelMultipleChoiceField(
        label='',
        queryset=MaidLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    consent = forms.BooleanField(
        label="""
            By submitting this enquiry form, I consent to the collection,
            use and disclosure of my personal data by Online Maid Pte Ltd to
            agencies that are listed on this platform.
        """
    )

    # captcha = ReCaptchaField(
    #     widget=ReCaptchaV3
    # )

    class Meta:
        model = GeneralEnquiry
        exclude = ['potential_employer', 'last_modified', 'date_published']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': ''
                }
            ),
            'mobile_number': forms.TextInput(
                attrs={
                    'placeholder': ''
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'placeholder': ''
                }
            ),
            'no_of_family_members': forms.NumberInput(
                attrs={
                    'placeholder': ''
                }
            ),
            'no_of_below_5': forms.NumberInput(
                attrs={
                    'placeholder': ''
                }
            ),
            'no_of_babies': forms.NumberInput(
                attrs={
                    'placeholder': ''
                }
            ),
            'remarks': OMCustomTextarea
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    css_class='form-group col-md-12 pr-md-3'
                ),
                Column(
                    'mobile_number',
                    css_class='form-group col-md-12 pl-md-3'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'email',
                    css_class='form-group col-md-12 pr-md-3'
                ),
                Column(
                    'property_type',
                    css_class='form-group col-md-12 pl-md-3'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'no_of_family_members',
                    css_class='form-group col-md-12 pr-md-3'
                ),
                Column(
                    'no_of_below_5',
                    css_class='form-group col-md-12 pl-md-3'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h6>Maid\'s Nationality</h6>'
                            )
                        ),
                        Column(
                            Field(
                                'maid_nationality',
                                template='widgets/custom_multi_choice_field.html'
                            ),
                            css_class='form-group col-24'
                        ),
                        css_class='form-row'
                    ),
                    css_class='col-lg-24'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h6>Type of Maid</h6>'
                            )
                        ),
                        Column(
                            Field(
                                'maid_type',
                                template='widgets/custom_multi_choice_field.html'
                            ),
                            css_class='form-group col-24'
                        ),
                        css_class='form-row'
                    ),
                    css_class='col-lg-24'
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h6>Job Responsibility</h6>'
                            )
                        ),
                        Column(
                            Field(
                                'maid_responsibility',
                                template='widgets/custom_multi_choice_field.html'
                            ),
                            css_class='form-group col-24'
                        ),
                        css_class='form-row'
                    ),
                    css_class='col-lg-24'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                '<h6>Spoken Language</h6>'
                            )
                        ),
                        Column(
                            Field(
                                'languages_spoken',
                                template='widgets/custom_multi_choice_field.html'
                            ),
                            css_class='form-group col-24'
                        ),
                        css_class='form-row'
                    ),
                    css_class='col-lg-24'
                )
            ),
            Row(
                Column(
                    'remarks',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            # Row(
            #     Column(
            #         Field(
            #             'captcha',
            #             type='hidden'
            #         ),
            #         css_class='form-group col'
            #     ),
            #     css_class='form-row'
            # ),
            Row(
                Column(
                    'consent',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-xs-lg btn-primary w-100 w-md-50"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row'
            )
        )


class ShortlistedEnquiryForm(forms.ModelForm):
    consent = forms.BooleanField(
        label="""
            By submitting this enquiry form, I consent to the collection,
            use and disclosure of my personal data by Online Maid Pte Ltd to
            agencies that are listed on this platform.
        """
    )

    class Meta:
        model = ShortlistedEnquiry
        exclude = ['potential_employer', 'maids', 'last_modified']
        widgets = {
            'remarks': forms.Textarea(
                attrs={
                    'rows': 8,
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
                    'name',
                    css_class='form-group'
                ),
                Column(
                    'mobile_number',
                    css_class='form-group'
                )
            ),
            Row(
                Column(
                    'email',
                    css_class='form-group'
                ),
                Column(
                    'property_type',
                    css_class='form-group'
                )
            ),
            Row(
                Column(
                    'no_of_family_members',
                    css_class='form-group'
                ),
                Column(
                    'no_of_below_5',
                    css_class='form-group'
                )
            ),
            Row(
                Column(
                    'remarks',
                    css_class='form-group'
                )
            ),
            Row(
                Column(
                    'consent',
                    css_class='form-group col'
                )
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-xs-lg btn-primary w-100 w-md-50"
                    ),
                    css_class='form-group text-center'
                )
            )
        )
