# Imports from django
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

# Imports from local apps
from .models import Advertisement

# Start of Forms

# Model Forms
class AgencyCreationForm(forms.ModelForm):
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
                    css_class='form-group col-md-6'
                ),
                Column(
                    'ad_type',
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

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        UserModel = get_user_model()
        if UserModel.objects.get(email=email):
            msg = _('This email is taken')
            self.add_error('email', msg)

# Generic Forms (forms.Form)