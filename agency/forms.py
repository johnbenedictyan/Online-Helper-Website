# Imports from django
from django import forms
from django.core.mail import BadHeaderError, send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.urls.base import reverse_lazy
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML

# Imports from local apps
from employer_documentation.models import EmployerDoc
from .constants import OpeningHoursTypeChoices
from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOpeningHours, AgencyOwner, PotentialAgency
)

# Start of Forms

# Forms that inherit from inbuilt Django forms

# Model Forms
class AgencyForm(forms.ModelForm):
    main_branch_name = forms.CharField(
        label=_('Branch Name'),
        max_length=100,
        required=False
    )
    
    main_branch_address_1 = forms.CharField(
        label=_('Address Line 1'),
        max_length=100,
        required=True
    )
    
    main_branch_address_2 = forms.CharField(
        label=_('Address Line 2'),
        max_length=100,
        required=True
    )
    
    main_branch_postal_code = forms.CharField(
        label=_('Postal Code'),
        max_length=100,
        required=True
    )
    
    main_branch_email = forms.CharField(
        label=_('Email'),
        max_length=100,
        required=True
    )
    
    main_branch_office_number = forms.CharField(
        label=_('Office No'),
        max_length=100,
        required=True
    )
    
    main_branch_mobile_number = forms.CharField(
        label=_('Mobile Number'),
        max_length=100,
        required=True
    )
    
    opening_hours_type = forms.ChoiceField(
        label=_('Agency\'s operating hours type'),
        required=True,
        choices=OpeningHoursTypeChoices.choices,
    )

    opening_hours_monday = forms.CharField(
        label=_('Monday\'s opening hours'),
        max_length=30,
        required=False
    )

    opening_hours_tuesday = forms.CharField(
        label=_('Tuesday\'s opening hours'),
        max_length=30,
        required=False
    )

    opening_hours_wednesday = forms.CharField(
        label=_('Wednesday\'s opening hours'),
        max_length=30,
        required=False
    )

    opening_hours_thursday = forms.CharField(
        label=_('Thursday\'s opening hours'),
        max_length=30,
        required=False
    )

    opening_hours_friday = forms.CharField(
        label=_('Friday\'s opening hours'),
        max_length=30,
        required=False
    )

    opening_hours_saturday = forms.CharField(
        label=_('Saturday\'s opening hours'),
        max_length=30,
        required=False
    )

    opening_hours_sunday = forms.CharField(
        label=_('Sunday\'s opening hours'),
        max_length=30,
        required=False
    )

    opening_hours_public_holiday = forms.CharField(
        label=_('Public holiday opening hours'),
        max_length=30,
        required=False
    )
    
    class Meta:
        model = Agency
        fields = ['name', 'license_number', 'website_uri', 'logo',
                  'profile', 'services']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h5 class="fs-2">Agency Information</h5>'
                    )
                ),
                css_class='row',
                css_id='agencyInformationGroup'
            ),
            Div(
                Column(
                    'logo',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'license_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'website_uri',
                    css_class='form-group col-md-6'
                ),
                css_class='row form-group mb-xl-3'
            ),
            Div(
                Column(
                    HTML(
                        '<h5>Main Outlet Details</h5>'
                    )
                ),
                css_class='row',
                css_id='agencyOutletDetailsGroup'
            ),
            Div(
                Column(
                    'main_branch_name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'main_branch_address_1',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'main_branch_address_2',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'main_branch_postal_code',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'main_branch_email',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'main_branch_office_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'main_branch_mobile_number',
                    css_class='form-group col-md-6'
                ),
                css_class='row form-group mb-xl-3'
            ),
            Div(
                Column(
                    HTML(
                        '<h5>Opening Hours</h5>'
                    )
                ),
                css_class='row',
                css_id='agencyOpeningHoursGroup'
            ),
            Div(
                Column(
                    'opening_hours_type',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_monday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_tuesday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_wednesday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_thursday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_friday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_saturday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_sunday',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'opening_hours_public_holiday',
                    css_class='form-group col-md-6'
                ),
                css_class='row form-group mb-xl-3'
            ),
            Div(
                Div(
                    Div(
                        Column(
                            HTML(
                                '<h5>Profile</h5>'
                            )
                        ),
                        css_class='row',
                        css_id='agencyProfileGroup'
                    ),
                    Div(
                        Column(
                            'profile'
                        ),
                        css_class='row form-group mb-xl-3'
                    ),
                    css_class='col'
                ),
                Div(
                    Div(
                        Column(
                            HTML(
                                '<h5>Our Services</h5>'
                            )
                        ),
                        css_class='row',
                        css_id='agencyServicesGroup'
                    ),
                    Div(
                        Column(
                            'services'
                        ),
                        css_class='row form-group mb-xl-3'
                    ),
                    css_class='col'
                ),
                css_class='row'
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
        return cleaned_data
    
    def save(self, *args, **kwargs):
        cleaned_data = self.cleaned_data
        new_agency = super().save()
        AgencyBranch.objects.create(
            agency=new_agency,
            name=cleaned_data.get('main_branch_name'),
            address_1=cleaned_data.get('main_branch_address_1'),
            address_2=cleaned_data.get('main_branch_address_2'),
            postal_code=cleaned_data.get('main_branch_postal_code'),
            office_number=cleaned_data.get('main_branch_office_number'),
            mobile_number=cleaned_data.get('main_branch_mobile_number'),
            main_branch=True
        )
        
        AgencyOpeningHours.objects.create(
            agency=new_agency,
            type=cleaned_data.get('opening_hours_type'),
            monday=cleaned_data.get('opening_hours_monday'),
            tuesday=cleaned_data.get('opening_hours_tuesday'),
            wednesday=cleaned_data.get('opening_hours_wednesday'),
            thursday=cleaned_data.get('opening_hours_thursday'),
            friday=cleaned_data.get('opening_hours_friday'),
            saturday=cleaned_data.get('opening_hours_saturday'),
            sunday=cleaned_data.get('opening_hours_sunday'),
            public_holiday=cleaned_data.get('opening_hours_public_holiday')
        )
        return new_agency

class AgencyUpdateForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = [
            'name', 'license_number', 'website_uri', 'logo', 'profile', 
            'services'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile'].label = ""
        self.fields['services'].label = ""
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h5 class="fs-2">Agency Information</h5>'
                    )
                ),
                css_class='row',
                css_id='agencyInformationGroup'
            ),
            Row(
                Column(
                    'logo',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'name',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'license_number',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'website_uri',
                    css_class='form-group col-md-6'
                ),
                css_class='mb-xl-3'
            ),
            Row(
                Column(
                    HTML(
                        '<h5 class="fs-2">Profile</h5>'
                    ),
                    'profile',
                    css_class='form-group col-md-6',
                    css_id='agencyProfileGroup'
                ),
                Column(
                    HTML(
                        '<h5 class="fs-2">Our Services</h5>'
                    ),
                    'services',
                    css_class='form-group col-md-6',
                    css_id='agencyServicesGroup'
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
                    'name',
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

class AgencyEmployeeForm(forms.ModelForm):
    pk = None
    agency_id = None
    authority = None
    form_type = None
    
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
        self.form_type = kwargs.pop('form_type')
        self.agency_id = kwargs.pop('agency_id')
        self.authority = kwargs.pop('authority')
        
        if self.form_type == 'update':
            self.pk = kwargs.pop('pk')
            
        super().__init__(*args, **kwargs)
        branch_list = AgencyBranch.objects.filter(
            agency = Agency.objects.get(
                pk = self.agency_id
            )
        )
        
        if self.form_type == 'create':
            self.fields['branch'].queryset = branch_list
            self.fields['branch'].initial = branch_list[0]
            self.fields['ea_personnel_number'].initial = ''
        
        if self.form_type == 'update':
            self.fields['password'].required = False
            self.fields['password'].help_text = _(
                'Enter a new password if you wish to change your password'
            )
            if self.authority == 'employee':
                self.fields['ea_personnel_number'].disabled = True
                self.fields['branch'].disabled = True
                self.fields['role'].disabled = True
            
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h5 class="fs-2">Employee Information</h5>'
                    )
                ),
                css_class='row',
                css_id='employeeInformationGroup'
            ),
            Row(
                Column(
                    'name',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'ea_personnel_number',
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
                    'email',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'contact_number',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'branch',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'role',
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
            if self.form_type == 'create':
                msg = _('This email is taken')
                self.add_error('email', msg)

        if self.form_type == 'create':
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
        email = cleaned_data.get("email")
        
        if self.form_type == 'update':
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

            if self.changed_data:
                if 'name' in self.changed_data or 'ea_personnel_number' in self.changed_data:
                    employer_doc_qs = EmployerDoc.objects.filter(
                        employer__agency_employee=self.instance
                    )
                    for employer_doc in employer_doc_qs:
                        employer_doc.increment_version_number()

        else:
            try:
                new_user = get_user_model().objects.create_user(
                    email=email,
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
        self.instance.name = cleaned_data.get('name')
        self.instance.contact_number = cleaned_data.get('contact_number')
        self.instance.ea_personnel_number = cleaned_data.get(
            'ea_personnel_number'
        )
        self.instance.branch = cleaned_data.get('branch')
        self.instance.role = cleaned_data.get('role')
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
        branch_name = cleaned_data.get('name')
        main_branch = cleaned_data.get("main_branch")
        try:
            current_main_branch = AgencyBranch.objects.get(
                agency=self.agency,
                main_branch=True
            )
        except AgencyBranch.DoesNotExist:
            if main_branch == False:
                msg = _('You must have at least one main branch')
                self.add_error('main_branch', msg)
        else:
            if main_branch == True and branch_name != current_main_branch.name:
                msg = _(f"""
                    {current_main_branch} is already set as the main branch
                """)
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
        self.agency_id = kwargs.pop('agency_id')
        self.agency = Agency.objects.get(
            pk=self.agency_id
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
                                <button class="btn btn-outline-primary 
                                                eh-delete-button"
                                        data-rowNumber="1"
                                >
                                    <i class="fas fa-times"></i>
                                </button>'''
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            'name',
                            css_class='col-md-6'
                        ),
                        Column(
                            'address_1',
                            css_class='col-md-6'
                        ),
                        Column(
                            'address_2',
                            css_class='col-md-6'
                        ),
                        Column(
                            'postal_code',
                            css_class='col-md-6'
                        ),
                        Column(
                            'email',
                            css_class='col-md-6'
                        ),
                        Column(
                            'office_number',
                            css_class='col-md-6'
                        ),
                        Column(
                            'mobile_number',
                            css_class='col-md-6'
                        ),
                        Column(
                            'main_branch',
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class='form-group',
            )
        )

class AgencyOpeningHoursForm(forms.ModelForm):
    class Meta:
        model = AgencyOpeningHours
        exclude = ['agency']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monday_start'].label = ""
        self.fields['monday_end'].label = ""
        self.fields['monday_closed'].label = "Closed"
        self.fields['tuesday_start'].label = ""
        self.fields['tuesday_end'].label = ""
        self.fields['tuesday_closed'].label = "Closed"
        self.fields['wednesday_start'].label = ""
        self.fields['wednesday_end'].label = ""
        self.fields['wednesday_closed'].label = "Closed"
        self.fields['thursday_start'].label = ""
        self.fields['thursday_end'].label = ""
        self.fields['thursday_closed'].label = "Closed"
        self.fields['friday_start'].label = ""
        self.fields['friday_end'].label = ""
        self.fields['friday_closed'].label = "Closed"
        self.fields['saturday_start'].label = ""
        self.fields['saturday_end'].label = ""
        self.fields['saturday_closed'].label = "Closed"
        self.fields['sunday_start'].label = ""
        self.fields['sunday_end'].label = ""
        self.fields['sunday_closed'].label = "Closed"
        self.fields['public_holiday_start'].label = ""
        self.fields['public_holiday_end'].label = ""
        self.fields['public_holiday_closed'].label = "Closed"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Column(
                    HTML(
                        '<h5 class="fs-2">Opening Hours</h5>'
                    )
                ),
                css_class='row'
            ),
            Row(
                Column(
                    'type',
                    css_class='form-group col-md-6'
                )
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Monday</label>'
                ),
                Div(
                    'monday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'monday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'monday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Tuesday</label>'
                ),
                Div(
                    'tuesday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'tuesday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'tuesday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Wednesday</label>'
                ),
                Div(
                    'wednesday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'wednesday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'wednesday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Thursday</label>'
                ),
                Div(
                    'thursday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'thursday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'thursday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Friday</label>'
                ),
                Div(
                    'friday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'friday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'friday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Saturday</label>'
                ),
                Div(
                    'saturday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'saturday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'saturday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Sunday</label>'
                ),
                Div(
                    'sunday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'sunday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'sunday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Div(
                HTML(
                    '<label class="col-sm col-form-label">Public Holidays</label>'
                ),
                Div(
                    'public_holiday_start',
                    css_class='col-sm-4'
                ),
                Div(
                    HTML(
                        '-',
                    ),
                    css_class='col-0-5 form-group text-center align-self-center'
                ),
                Div(
                    'public_holiday_end',
                    css_class='col-sm-4'
                ),
                Div(
                    'public_holiday_closed',
                    css_class='col-sm-2'
                ),
                css_class="row form-group openingHourGroup"
            ),
            Row(
                Column(
                    HTML(
                        '''
                        <a href="{% url 'dashboard_agency_outlet_details_update' %}"
                        class="btn btn-outline-primary w-25 mx-2">Back</a>
                        '''
                    ),
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-primary w-25 mx-2"
                    ),
                    css_class='form-group col-12 text-center'
                )
            )
        )

class PotentialAgencyForm(forms.ModelForm):
    terms_and_conditions = forms.BooleanField()
    
    placeholders = {
        'name': 'Test Agency',
        'license_number': 'abc123',
        'person_in_charge': 'John Doe',
        'contact_number': '98765432',
        'office_number': '61234567',
        'email': 'john@testagency.com'
    }
    
    class Meta:
        model = PotentialAgency
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['terms_and_conditions'].label = f'''
            I agree to the 
            <a href="{reverse_lazy('terms_and_conditions')}" target="_blank">
                terms of service
            </a> 
            as well as the 
            <a href="{reverse_lazy('privacy_policy')}" target="_blank">
                privacy policy
            </a> of Online Maid
        '''
        for k, v in self.placeholders.items():
            self.fields[k].widget.attrs['placeholder'] = v
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    css_class='form-group col-md-6 pr-3'
                ),
                Column(
                    'license_number',
                    css_class='form-group col-md-6 pl-3'
                )
            ),
            Row(
                Column(
                    'person_in_charge',
                    css_class='form-group col-md-6 pr-3'
                ),
                Column(
                    'email',
                    css_class='form-group col-md-6 pl-3'
                )
            ),
            Row(
                Column(
                    'contact_number',
                    css_class='form-group col-md-6 pr-3'
                ),
                Column(
                    'office_number',
                    css_class='form-group col-md-6 pl-3'
                ),
            ),
            Row(
                Column(
                    'terms_and_conditions',
                    css_class='form-group col'
                )
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-primary w-100"
                    ),
                    css_class='form-group col-12 text-center'
                )
            )
        )

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        try:
            Agency.objects.get(
                license_number=license_number
            )
        except Agency.DoesNotExist as e:
            pass
        else:
            msg = _('This license number is taken')
            self.add_error('license_number', msg)
        return license_number
    
    def clean_terms_and_conditions(self):
        terms_and_conditions = self.cleaned_data.get('terms_and_conditions')
        if terms_and_conditions == False:
            msg = -('You must agree to sign up for our services')
            self.add_error('terms_and_conditions', msg)
            
        return terms_and_conditions

    def save(self, *args, **kwargs):
        # There is a cleaner way to write this save method
        cleaned_data = self.cleaned_data

        pa_name = cleaned_data.get('name')
        pa_license_number = cleaned_data.get('license_number')
        pa_person_in_charge = cleaned_data.get('person_in_charge')
        pa_contact_number = cleaned_data.get('contact_number')
        pa_office_number = cleaned_data.get('office_number')
        pa_email = cleaned_data.get('email')

        if pa_email:
            try:
                send_mail(
                    'New Agency Registration',
                    f"""
                    Name: {pa_name}
                    License Number: {pa_license_number}
                    Person In Charge: {pa_person_in_charge}
                    Contact Number: {pa_contact_number}
                    Office Number: {pa_office_number}
                    Email Address: {pa_email}
                    """,
                    settings.EMAIL_HOST_USER,
                    settings.EMAIL_HOST_SALES_USER
                )
            except BadHeaderError:
                msg = _('There is an error in this email. Please try again')
                self.add_error('email', msg)

        return super().save(*args, **kwargs)    
