# Imports from the system
import random
import string
import os

# Imports from django
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

# Imports from foreign installed apps

# Imports from local app
from .forms import EmployerCreationForm, SignInForm, AgencySignInForm
from .models import Employer
from .mixins import VerifiedEmployerMixin

# Start of Tests

## Helper Functions
UserModel = get_user_model()
def create_test_user():
    r_str = ''.join(
        random.choice(string.ascii_lowercase) for i in range(4)
    )
    return get_user_model().objects.create_user(
        email=f'{r_str}@{r_str}.com',
        password=f'{os.random(10)}'
    )

def create_test_potential_employer():
    new_user = create_test_user()
    employer_group = Group.objects.get(
        name='Employers'
    ) 
    employer_group.user_set.add(
        new_user
    )

    