# Django Imports
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

# Foreign Apps Imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div

# Project Apps Imports
from onlinemaid.constants import AG_OWNERS, P_EMPLOYERS

# App Imports
from .models import PotentialEmployer

# Start of Forms


class SignInForm(AuthenticationForm):
    # This is done because the success_url in the loginview does not seem
    # to override the default settings.login_redirect_url which is
    # accounts.profile

    # Will need to see if this affects the next url when passed in from a
    # mixin like login required

    # We cannot have it to be a static redirect, the next url must take
    # precedence
    # redirect_named_url = 'home'
    placeholders = {
        'username': '',
        'password': ''
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.placeholders.items():
            self.fields[k].widget.attrs['placeholder'] = v
        # self.fields['password'].help_text = '''
        #     <a class='ml-1'
        #     href="{% url 'password_reset' %}">Forget your password?</a>
        # '''
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'username',
                    css_class='form-group col-24'
                )
            ),
            Row(
                Column(
                    'password',
                    css_class='form-group col-24 mb-0'
                ),
                Column(
                    HTML("""<a class='ml-1 fs-11'
            href="{% url 'password_reset' %}">Forget your password?</a>"""),
                    css_class="mb-3")
            ),
            # Row(
            #     Column(
            #         Hidden(
            #             'next',
            #             f"{{% url '{self.redirect_named_url}' %}}"
            #         )
            #     ),
            #     css_class='form-row'
            # ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Login',
                        css_class="btn btn-xs-lg btn-primary w-100"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row'
            ),
        )


class AgencySignInForm(AuthenticationForm):
    # This is done because the success_url in the loginview does not seem
    # to override the default settings.login_redirect_url which is
    # accounts.profile

    # Will need to see if this affects the next url when passed in from a
    # mixin like login required

    # We cannot have it to be a static redirect, the next url must take
    # precedence
    # redirect_named_url = 'dashboard_home'

    agency_license_number = forms.CharField(
        label=_('Agency License Number'),
        required=True,
        max_length=255
    )

    username = forms.CharField(
        label=_('Email'),
        required=True,
        max_length=255
    )

    placeholders = {
        'agency_license_number': '',
        'username': '',
        'password': ''
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.placeholders.items():
            self.fields[k].widget.attrs['placeholder'] = v
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML(
                        '<h5 class="fs-16">Employment Agency Login</h5>'
                    ),
                    css_class='col mb-md-2 mb-lg-3 mb-xl-4'
                ),
                css_class='row'
            ),
            Row(
                Column(
                    'agency_license_number',
                    css_class='form-group col-md-12 pr-md-3'
                ),
                Column(
                    'username',
                    css_class='form-group col-md-12 pl-md-3'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'password',
                    css_class='form-group col-md-12 pr-md-3 mb-0'
                ),
                Column(
                    HTML("""<a class='ml-1 fs-11'
            href="{% url 'password_reset' %}">Forget your password?</a>"""),
                    css_class="col-24 mb-3"),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Login',
                        css_class="btn btn-xs-lg btn-primary w-100 w-md-30"
                    ),
                    css_class='form-group col-24 text-center'
                ),
                css_class='form-row'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        UserModel = get_user_model()
        username = cleaned_data.get('username')
        try:
            user = UserModel.objects.get(
                email=username
            )
        except UserModel.DoesNotExist:
            pass
        else:
            if user.groups.filter(name=P_EMPLOYERS).exists():
                self.add_error(
                    'username',
                    ValidationError(
                        _('Invalid Agency Staff Registration Number'),
                        code='invalid-signin'
                    )
                )

            if user.groups.filter(name=AG_OWNERS).exists():
                agency = user.agency_owner.agency
            else:
                agency = user.agency_employee.agency

            if (
                agency.license_number != cleaned_data.get(
                    'agency_license_number'
                )
            ):
                self.add_error(
                    'agency_license_number',
                    ValidationError(
                        _('Invalid Agency License Number'),
                        code='invalid-signin'
                    )
                )
            if not agency.active:
                self.add_error(
                    'agency_license_number',
                    ValidationError(
                        _(
                            '''This agency has been deactivate.
                            Please contact Online Maid Pte Ltd.'''),
                        code='invalid-signin'
                    )
                )
        return cleaned_data


class EmployerCreationForm(forms.ModelForm):
    email = forms.CharField(
        label=_('Email Address'),
        required=True,
        max_length=255
    )

    password = forms.CharField(
        label=_('Password'),
        required=True,
        max_length=255,
        widget=forms.PasswordInput()
    )

    terms_and_conditions = forms.BooleanField()

    placeholders = {
        'email': '',
        'password': ''
    }

    class Meta:
        model = PotentialEmployer
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        self.form_type = kwargs.pop('form_type', None)
        super().__init__(*args, **kwargs)
        if self.form_type == 'UPDATE':
            kwargs.update(initial={
                'email': kwargs.pop('email_address', None)
            })
        else:
            for k, v in self.placeholders.items():
                self.fields[k].widget.attrs['placeholder'] = v
        self.fields['terms_and_conditions'].label = f'''
            I agree to the
            <a href="{
                reverse_lazy('terms_and_conditions_user')
            }" target="_blank">
                terms of service
            </a>
            as well as the
            <a href="{reverse_lazy('privacy_policy')}" target="_blank">
                privacy policy
            </a> of Online Maid
        '''
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'email',
                    css_class='form-group col-24'
                ),
                Column(
                    'password',
                    css_class='form-group col-24'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'terms_and_conditions',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Create',
                        css_class="btn btn-xs-lg btn-primary w-100"
                    ),
                    css_class='col-24 text-center'
                ),
                css_class='form-row'
            )
        )

    def clean_terms_and_conditions(self):
        terms_and_conditions = self.cleaned_data.get('terms_and_conditions')
        if not terms_and_conditions:
            msg = -('You must agree to sign up for our services')
            self.add_error('terms_and_conditions', msg)

        return terms_and_conditions

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        UserModel = get_user_model()
        try:
            UserModel.objects.get(
                email=email
            )
        except UserModel.DoesNotExist:
            pass
        else:
            msg = _('This email is taken')
            self.add_error('email', msg)

        if validate_password(password):
            msg = _('This password does not meet our requirements')
            self.add_error('password', msg)

        return cleaned_data

    def save(self, *args, **kwargs):
        cleaned_data = super().clean()
        try:
            new_user = get_user_model().objects.create_user(
                email=cleaned_data.get('email'),
                password=cleaned_data.get('password')
            )
        except Exception:
            pass
        else:
            potential_employer_group = Group.objects.get(
                name='Potential Employers'
            )
            potential_employer_group.user_set.add(
                new_user
            )
            self.instance.user = new_user
            return super().save(*args, **kwargs)


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Email Address'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'email',
                    css_class='form-group'
                )
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Send',
                        css_class="btn btn-xs-lg btn-primary w-100"
                    ),
                    css_class='form-group col-24 text-center'
                )
            ),
        )


class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'email',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-xs-lg btn-primary w-50"
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

        try:
            UserModel.objects.get(
                email=email
            )
        except UserModel.DoesNotExist:
            pass
        else:
            msg = _('You must change the email address')
            self.add_error('email', msg)

        return cleaned_data
