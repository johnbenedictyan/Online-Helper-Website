# Imports from the system
import random
import string

# Imports from django
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

# Imports from foreign installed apps

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
    return random.randint(80000000, 99999999)

def create_test_user():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_user_model().objects.create_user(
        email=f'{r_string(4)}@{r_string(4)}.com',
        password=f'{get_random_string(10, chars)}'
    )
