# Django Imports
from django import forms
from django.utils.translation import ugettext_lazy as _

# Foreign Apps Imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

# App Imports

# Start of Forms


class ContactUsFrom(forms.Form):
    MAID_NATIONALITY_CHOICES = (
        ('ALL', _('No preference')),
        ('KHM', _('Cambodian')),
        ('PHL', _('Filipino')),
        ('IND', _('Indian')),
        ('IDN', _('Indonesian')),
        ('MMR', _('Myanmarese')),
        ('LKA', _('Sri Lankan')),
        ('OTH', _('Others'))
    )

    MAID_MAIN_RESPONSIBILITY_CHOICES = (
        ('ALL', _('No preference')),
        ('GEH', _('General Housework')),
        ('COK', _('Cooking')),
        ('CFI', _('Care for Infants/Children')),
        ('CFE', _('Care for the Elderly')),
        ('CFD', _('Care for the Disabled'))
    )

    MAID_TYPE_CHOICES = (
        ('ALL', _('No preference')),
        ('NEW', _('No Experience')),
        ('TRA', _('Transfer')),
        ('SGE', _('Singapore Experience')),
        ('OVE', _('Overseas Experience'))
    )

    MAID_AGE_CHOICES = (
        (i, _(f'{i}')) for i in range(23, 51)
    )

    first_name = forms.CharField(
        label=_('First Name'),
        required=True,
        max_length=100
    )

    last_name = forms.CharField(
        label=_('Last Name'),
        required=True,
        max_length=100
    )

    contact_number = forms.CharField(
        label=_('Contact Number'),
        required=True,
        max_length=100
    )

    email = forms.EmailField(
        label=_('Email'),
        required=True,
        max_length=255
    )

    maid_nationality = forms.CharField(
        label=_('Maid\'s Nationality'),
        required=True,
        choices=MAID_NATIONALITY_CHOICES,
        max_length=3
    )

    maid_main_responsibility = forms.CharField(
        label=_('Maid\'s main responsibility'),
        required=True,
        choices=MAID_MAIN_RESPONSIBILITY_CHOICES,
        max_length=3
    )

    maid_type = forms.CharField(
        label=_('Type of maid'),
        required=True,
        choices=MAID_TYPE_CHOICES,
        max_length=3
    )

    maid_min_age = forms.ChoiceField(
        label=_('Minimum age of Maid'),
        required=True,
        choices=MAID_AGE_CHOICES,
        max_length=2
    )

    maid_max_age = forms.IntegerField(
        label=_('Maximum age of Maid'),
        required=True,
        choices=MAID_AGE_CHOICES,
        max_length=2
    )

    remarks = forms.CharField(
        label=_('Remarks'),
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 80,
                'cols': 20
                }
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
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
                    css_class='form-group col-md-4'
                ),
                Column(
                    'maid_main_responsibility',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'maid_type',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'maid_min_age',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'maid_max_age',
                    css_class='form-group col-md-6'
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
