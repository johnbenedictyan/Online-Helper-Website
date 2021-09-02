# Django Imports
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

# Foreign Apps Imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

# App Imports
from .models import Advertisement

# Start of Forms

# Model Forms


class AdvertisementCreationForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        exclude = ['agency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'location',
                    css_class='form-group col-md-12'
                ),
                Column(
                    'ad_type',
                    css_class='form-group col-md-12'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-xs-lg btn btn-xs-lg-primary w-50"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        UserModel = get_user_model()
        if UserModel.objects.get(email=email):
            msg = _('This email is taken')
            self.add_error('email', msg)
