# Imports from django
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Hidden
from onlinemaid.constants import (
    AG_OWNERS, AG_ADMINS, AG_MANAGERS, AG_SALES, P_EMPLOYERS
)

# Imports from local apps
from .managers import CustomUserManager
from .models import PotentialEmployer, User

# Start of Forms

# Forms that inherit from inbuilt Django forms
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
        'username': 'johndoe123',
        'password': 'topsecret'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for k, v in self.placeholders.items():
            self.fields[k].widget.attrs['placeholder'] = v
        self.fields['password'].help_text = '''
            <a class='ml-1' 
            href="{% url 'password_reset' %}">Forget your password?</a>
        '''
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'username',
                    css_class='form-group col-12'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'password',
                    css_class='form-group col-12'
                ),
                css_class='form-row'
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
                        'Log in',
                        css_class="btn btn-primary w-100"
                    ),
                    css_class='form-group col-12 text-center'
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
        label=_('Username'),
        required=True,
        max_length=255,
        help_text=_('''
            For Agency Owners use your email.
            For Agency Employees use your EA personnel registration number.'''
        )
    )

    placeholders = {
        'agency_license_number': 'abc123',
        'username': 'john@agency.com / johndoe123',
        'password': 'topsecret'
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for k, v in self.placeholders.items():
            self.fields[k].widget.attrs['placeholder'] = v
        self.fields['password'].help_text = '''
            <a class='ml-1' 
            href="{% url 'password_reset' %}">Forget your password?</a>
        '''
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'username',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'password',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'agency_license_number',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
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
                        'Log In',
                        css_class="btn btn-primary w-100"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            ),
        )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            validate_email(username)
        except:
            username = username + '@' + settings.AGENCY_EMPLOYEE_FEP

        return username

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
            if agency.active == False:
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

# Model Forms
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
    
    terms_of_service = forms.BooleanField()

    placeholders = {
        'email': 'johndoe@example.com',
        'password': 'topsecret',
        'name': 'John Doe',
        'contact_number': '81234567'
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
        self.fields['terms_of_service'].label = f'''
            I agree to the 
            <a href="{reverse_lazy('terms_of_service')}" target="_blank">
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
                    css_class='form-group col-md-6'
                ),
                Column(
                    'password',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'name',
                    css_class='form-group col'
                ),
                Column(
                    'contact_number',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'terms_of_service',
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
                    css_class='col-12 text-center'
                ),
                css_class='form-row'
            )
        )

    def clean_terms_of_service(self):
        terms_of_service = self.cleaned_data.get('terms_of_service')
        if terms_of_service == False:
            msg = -('You must agree to sign up for our services')
            self.add_error('terms_of_service', msg)
            
        return terms_of_service
    
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
        except Exception as e:
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

# Generic Forms (forms.Form)