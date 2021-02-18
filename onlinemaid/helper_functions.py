# Imports from the system
import random
import string
from datetime import date

# Imports from django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.crypto import get_random_string

# Imports from foreign installed apps
from maid.constants import MaidLanguageChoices, MaidResponsibilityChoices
from maid.models import MaidLanguage, MaidResponsibility
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from .constants import AUTHORITY_GROUPS

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
    email = f'{r_string(4)}@{r_string(4)}.com'
    password = f'{get_random_string(10, chars)}'
    return {
        'email': email,
        'password': password,
        'obj': get_user_model().objects.create_user(
            email=email,
            password=password
        )
    }

def encrypt_string(plaintext, encryption_key):
    # Data to be encrypted formatted as bytes literal
    bytes_literal = plaintext.encode('ascii')

    # Secret encryption key set in environment variables, does not change
    key = encryption_key.encode('ascii')

    # New nonce everytime
    nonce = get_random_bytes(32)
    
    # Create cipher object
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Generate encrypted ciphertext
    ciphertext, tag = cipher.encrypt_and_digest(bytes_literal)

    return ciphertext, nonce, tag

def decrypt_string(ciphertext, encryption_key, nonce, tag):
    cipher = AES.new(encryption_key.encode('ascii'), AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('ascii')

def calculate_age(born):
    today = date.today()
    offset = ((today.month, today.day) < (born.month, born.day))
    return today.year - born.year - offset

def populate_necessary_rows():
    for language in MaidLanguageChoices.choices:
        MaidLanguage.objects.get_or_create(
            language=language[0]
        )

    for responsibility in MaidResponsibilityChoices.choices:
        MaidResponsibility.objects.get_or_create(
            name=responsibility[0]
        )

    for AG in AUTHORITY_GROUPS:
        Group.objects.get_or_create(
            name=AG
        )