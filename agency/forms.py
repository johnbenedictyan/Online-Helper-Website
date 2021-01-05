# Imports from django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

# Imports from local apps
from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOperatingHours, AgencyPlan,
    AgencyOwner
)

# Start of Forms

# Forms that inherit from inbuilt Django forms

# Model Forms
class AgencyCreationForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'license_number',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'company_email',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'sales_email',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'uen',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'website_uri',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'logo',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'qr_code',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'mission',
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

class AgencyOwnerCreationForm(forms.ModelForm):
    email = forms.EmailField(
        label=_('Email Address'),
        required=True
    )

    password = forms.CharField(
        label=_('Password'),
        required=True,
        max_length=255,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = AgencyOwner
        exclude = ['user', 'agency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        password = cleaned_data.get("password")
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(
                email=email
            )
        except UserModel.DoesNotExist:
            pass
        else:
            msg = _('This email is taken by another user')
            self.add_error('email', msg)

        if validate_password(password):
            msg = _('This password does not meet our requirements')
            self.add_error('password', msg)
            
        return cleaned_data

    def save(self, *args, **kwargs):
        # There is a cleaner way to write this save method
        cleaned_data = self.cleaned_data
        try:
            new_user = get_user_model().objects.create_user(
                email=cleaned_data.get('email'),
                password=cleaned_data.get('password')
            )
        except Exception as e:
            pass
        else:
            agency_owner_group = Group.objects.get(
                name='Agency Owners'
            ) 
            agency_owner_group.user_set.add(
                new_user
            )

            self.instance.user = new_user

            return super().save(*args, **kwargs)

class AgencyEmployeeCreationForm(forms.ModelForm):
    email = forms.EmailField(
        label=_('Email Address'),
        required=True
    )

    password = forms.CharField(
        label=_('Password'),
        required=True,
        max_length=255,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = AgencyEmployee
        exclude = ['agency','user']

    def __init__(self, *args, **kwargs):
        # Limit the choices of the foreign key branch to just the branches
        # under the current agency
        agency_id = kwargs.pop('agency_id')
        super().__init__(*args, **kwargs)
        self.fields['branch'].queryset = AgencyBranch.objects.filter(
            agency = Agency.objects.get(
                pk = agency_id
            )
        )
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
                    'first_name',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'last_name',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'contact_number',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'ea_personnel_number',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'branch',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'role',
                    css_class='form-group col-md-4'
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
        password = cleaned_data.get("password")
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(
                email=email
            )
        except UserModel.DoesNotExist:
            pass
        else:
            if hasattr(user, 'agency'):
                msg = _('This user is already part of an agency')
            else:
                msg = _('This email is taken by an employer')
            self.add_error('email', msg)

        if validate_password(password):
            msg = _('This password does not meet our requirements')
            self.add_error('password', msg)
            
        return cleaned_data

    def save(self, *args, **kwargs):
        # There is a cleaner way to write this save method
        cleaned_data = self.cleaned_data
        role = cleaned_data.get('role')
        role_name_dict = {
            'AA': 'Agency Administrators',
            'AM': 'Agency Managers',
            'AS': 'Agency Sales Staff'
        }
        try:
            new_user = get_user_model().objects.create_user(
                email=cleaned_data.get('email'),
                password=cleaned_data.get('password')
            )
        except Exception as e:
            pass
        else:
            agency_employee_group = Group.objects.get(
                name=role_name_dict[role]
            ) 
            agency_employee_group.user_set.add(
                new_user
            )

            self.instance.user = new_user
            self.instance.first_name = cleaned_data.get('first_name')
            self.instance.last_name = cleaned_data.get('last_name')
            self.instance.contact_number = cleaned_data.get(
                'contact_number'
            )
            self.instance.ea_personnel_number = cleaned_data.get(
                'ea_personnel_number'
            )
            self.instance.branch = cleaned_data.get('branch')
            self.instance.role = cleaned_data.get('role')

            return super().save(*args, **kwargs)

class AgencyEmployeeUpdateForm(forms.ModelForm):
    pk = None
    agency_id = None
    authority = None

    email = forms.EmailField(
        label=_('Email Address'),
        required=True
    )

    password = forms.CharField(
        label=_('Password'),
        required=False,
        max_length=255,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = AgencyEmployee
        exclude = ['agency','user']

    def __init__(self, *args, **kwargs):
        # Limit the choices of the foreign key branch to just the branches
        # under the current agency
        self.agency_id = kwargs.pop('agency_id')
        self.pk = kwargs.pop('pk')
        self.authority = kwargs.pop('authority')
        super().__init__(*args, **kwargs)
        self.fields['branch'].queryset = AgencyBranch.objects.filter(
            agency = Agency.objects.get(
                pk = self.agency_id 
            )
        )
        if self.authority == 'employee':
            self.fields['ea_personnel_number'].disabled = True
            self.fields['branch'].disabled = True
            self.fields['role'].disabled = True

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
                    'first_name',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'last_name',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'contact_number',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'ea_personnel_number',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'branch',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'role',
                    css_class='form-group col-md-4'
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

    # This from is used when the agency employee details are being updated
    # It has a different clean and save method thatn the creation form

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(
                email=email
            )
        except UserModel.DoesNotExist:
            pass
        else:
            if not user.pk == self.pk:
                msg = _('This email is taken')
                self.add_error('email', msg)

        if password and validate_password(password):
            msg = _('This password does not meet our requirements')
            self.add_error('password', msg)
            
        return cleaned_data

    def save(self, *args, **kwargs):
        # There is a cleaner way to write this save method
        cleaned_data = self.cleaned_data
        role = cleaned_data.get('role')
        role_name_dict = {
            'AA': 'Agency Administrators',
            'AM': 'Agency Managers',
            'AS': 'Agency Sales Staff'
        }
        employee = AgencyEmployee.objects.get(
            pk = self.pk
        )

        old_agency_employee_group = Group.objects.get(
            name=role_name_dict[employee.role]
        ) 

        new_agency_employee_group = Group.objects.get(
            name=role_name_dict[role]
        ) 

        if self.instance.user.email != cleaned_data.get('email'):
            employee.user.email = cleaned_data.get('email')
            employee.user.save()
        
        if cleaned_data.get('password'):
            employee.user.set_password(cleaned_data.get('password'))
            employee.user.save()

        if old_agency_employee_group != new_agency_employee_group:
            old_agency_employee_group.user_set.remove(employee.user)
            new_agency_employee_group.user_set.add(employee.user)

        self.instance.user = employee.user
        self.instance.first_name = cleaned_data.get('first_name')
        self.instance.last_name = cleaned_data.get('last_name')
        self.instance.contact_number = cleaned_data.get(
            'contact_number'
        )
        self.instance.ea_personnel_number = cleaned_data.get(
            'ea_personnel_number'
        )
        self.instance.branch = cleaned_data.get(
            'branch'
        )
        self.instance.role = cleaned_data.get(
            'role'
        )

        return super().save(*args, **kwargs)

class AgencyBranchForm(forms.ModelForm):
    class Meta:
        model = AgencyBranch
        exclude = ['agency', 'area']
        widgets = {
            'main_branch': forms.RadioSelect()
        }
    
    def clean(self):
        cleaned_data = super().clean()
        main_branch = cleaned_data.get("main_branch")
        self.agency = Agency.objects.get(
            pk=self.agency_id
        )
        branches = AgencyBranch.objects.filter(
            agency=self.agency
        )
        main_branch_counter = 0
        current_main_branch = None
        for branch in branches:
            if branch.main_branch == True:
                current_main_branch = branch.name
                main_branch_counter += 1

        if main_branch_counter > 0 and main_branch == True:
            if self.form_type == 'CREATE':
                if current_main_branch:
                    msg = _(f"""
                        {current_main_branch} is already set as the main branch
                    """)
                else:
                    msg = _('There can only be one main branch')
                self.add_error('main_branch', msg)

        elif main_branch_counter == 0 and main_branch == False:
            msg = _('You must have at least one main branch')
            self.add_error('main_branch', msg)
        return cleaned_data

    def save(self, *args, **kwargs):
        CENTRAL = 'C'
        NORTH = 'N'
        NORTH_EAST = 'NE'
        EAST = 'E'
        WEST = 'W'

        postal_code_area_dict = {
            CENTRAL : [
                '01','02','03','04','05','06','07','08','09','10','14','15',
                '16','17','18','19','20','21','22','23','24','25','26','27',
                '28','29','30','31','32','33','34','35','36','37','38','39',
                '40','41','58','59','77','78'
            ],
            NORTH : [
                '69','70','71','72','73','75','76'
            ],
            NORTH_EAST : [
                '53','54','55','56','57','79','80','82'
            ],
            EAST : [
                '42','43','44','45','46','47','48','49','50','51','52','81'
            ],
            WEST : [
                '11','12','13','60','61','62','63','64','65','66','67','68'
            ]
        }
        cleaned_data = self.cleaned_data
        postal_code = cleaned_data.get('postal_code')
        for k,v in postal_code_area_dict.items():
            if str(postal_code[:2]) in v:
                self.instance.area = k

        self.instance.agency = self.agency
        return super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.agency_id = kwargs.pop('agency_id', None)
        self.form_type = kwargs.pop('form_type', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    css_class='form-group col'
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
                    'postal_code',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'main_branch',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'office_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'mobile_number',
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

class AgencyOperatingHoursForm(forms.ModelForm):
    class Meta:
        model = AgencyOperatingHours
        exclude = ['agency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'operating_type',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'monday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'tuesday',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'wednesday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'thursday',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'friday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'saturday',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'sunday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'public_holiday',
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

class AgencyPlanForm(forms.ModelForm):
    class Meta:
        model = AgencyPlan
        exclude = ['agency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'choice',
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

# Generic Forms (forms.Form)