# Imports from django
from django import forms
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

# Imports from local apps

# Start of Forms

# Forms that inherit from inbuilt Django forms

# Model Forms

# Generic Forms (forms.Form)
class GeneralEnquiryForm(forms.Form):
    # FIELDS TO ADD for detailed:
    # Change main responsibility to responsibilites with a multi checkbox
    # Add care for pet and gardening in responsibilites
    
    # Change enquiry form to one form, all fields compulsory
    
    # Add property field
    # HDB: 2,3,4,5 executive/massionnette
    # condo: condo, penthouse
    # landed: terrace, semi-d, bungalow, others

    # Age group field
    # 23-29, 30-39, 40-49, above 50

    # number of rest day per month
    # 0 rest day per month
    # 1 rest day per month
    # 2 rest day per month
    # 3 rest day per month
    # 4 rest day per month

    # Number of family members in total residing
    # No of below 12 residing
    # No of baby residing

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
        (23, _('23')),
        (24, _('24')),
        (25, _('25')),
        (26, _('26')),
        (27, _('27')),
        (28, _('28')),
        (29, _('29')),
        (30, _('30')),
        (31, _('31')),
        (32, _('32')),
        (33, _('33')),
        (34, _('34')),
        (35, _('35')),
        (36, _('36')),
        (37, _('37')),
        (38, _('38')),
        (39, _('39')),
        (40, _('40')),
        (41, _('41')),
        (42, _('42')),
        (43, _('43')),
        (44, _('44')),
        (45, _('45')),
        (46, _('46')),
        (47, _('47')),
        (48, _('48')),
        (49, _('49')),
        (50, _('50'))
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

    maid_nationality = forms.ChoiceField(
        label=_('Maid\'s Nationality'),
        required=True,
        choices=MAID_NATIONALITY_CHOICES
    )

    maid_main_responsibility = forms.ChoiceField(
        label=_('Maid\'s main responsibility'),
        required=True,
        choices=MAID_MAIN_RESPONSIBILITY_CHOICES
    )

    maid_type = forms.ChoiceField(
        label=_('Type of maid'),
        required=True,
        choices=MAID_TYPE_CHOICES
    )

    maid_min_age = forms.ChoiceField(
        label=_('Minimum age of Maid'),
        required=True,
        choices=MAID_AGE_CHOICES
    )

    maid_max_age = forms.ChoiceField(
        label=_('Maximum age of Maid'),
        required=True,
        choices=MAID_AGE_CHOICES
    )

    remarks = forms.CharField(
        label=_('Remarks'),
        required=True,
        widget=forms.Textarea(
            attrs={
                'rows': 20,
                'cols': 15
            }
        )
    )

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