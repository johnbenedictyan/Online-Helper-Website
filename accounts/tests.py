# Imports from the system
import random
import string
import os

# Imports from django
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

# Imports from foreign installed apps

# Imports from local app
from .forms import EmployerCreationForm, SignInForm, AgencySignInForm
from .models import Employer
from .mixins import VerifiedEmployerMixin

# Start of Tests

## Helper Functions
UserModel = get_user_model()

def r_string(length):
    r_str = ''.join(
        random.choice(string.ascii_lowercase) for i in range(length)
    )
    return r_str

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)

def r_contact_number():
    return random.randint(80000000, 9999999)

def create_test_user():
    return get_user_model().objects.create_user(
        email=f'{r_string(4)}@{r_string(4)}.com',
        password=f'{os.random(10)}'
    )

def create_potential_employer_group():
    potential_employers_group = Group.objects.get_or_create(
        name='Potential Employers'
    )

    pe_permission_list = [
        'change_employer',
        'delete_employer',
        'view_employer',
        'view_agency',
        'view_agencybranch',
        'view_agencyoperatinghours',
        'view_employerbase',
        'view_employerdocbase',
        'view_employerdocemploymentcontract',
        'view_employerdocjoborder',
        'view_employerdocmaidstatus',
        'view_employerdocserviceagreement',
        'view_employerdocservicefeebase',
        'view_employerdocservicefeereplacement',
        'view_employerdocsig',
        'view_employerextrainfo',
        'view_maid',
        'view_maidbiodata',
        'view_maidcooking',
        'view_maiddietaryrestriction',
        'view_maiddisabledcare',
        'view_maidelderlycare',
        'view_maidemploymenthistory',
        'view_maidfamilydetails',
        'view_maidfoodhandlingpreference',
        'view_maidgeneralhousework',
        'view_maidinfantchildcare',
        'view_maidworkduty',
        'view_invoice'
    ]

    for perm in pe_permission_list:
        potential_employers_group.permissions.add(
            Permission.objects.get(
                code_name=perm
            )
        )

def create_test_potential_employer():
    new_user = create_test_user()
    new_pe = Employer.objects.create(
        user=new_user,
        first_name=r_string(5),
        last_name=r_string(5),
        contact_number=r_contact_number()
    )
    pe_group = Group.objects.get(
        name='Potential Employers'
    ) 
    pe_group.user_set.add(
        new_user
    )

    return new_pe
    