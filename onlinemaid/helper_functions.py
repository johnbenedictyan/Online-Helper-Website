# Imports from the system
import math
import random
import string
import traceback
from datetime import date, datetime, timedelta

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.crypto import get_random_string
from slugify import slugify


from .constants import MaritalStatusChoices

UserModel = get_user_model()


def is_null(x) -> bool:
    return False if x else True


def is_not_null(x) -> bool:
    return not is_null(x)


def is_of_age(dt, age: int) -> bool:
    if dt and age:
        date_diff = date.today() - dt
        return date_diff.days >= age * 365


def is_pasted(dt) -> bool:
    if dt:
        return dt < date.today()


def slugify_text(text) -> str:
    return slugify(text)


def is_married(marital_status) -> bool:
    return marital_status == MaritalStatusChoices.MARRIED


def r_string(length) -> str:
    r_str = ''.join(
        random.choice(string.ascii_lowercase) for i in range(length)
    )
    return r_str


def r_contact_number() -> int:
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
    bytes_literal = plaintext.upper().encode('ascii')

    # Secret encryption key set in environment variables, does not change
    '''
    E.g. to generate 32 byte (256 bit) key, run following command in bash
    shell:
    python3 -c "import secrets; print(secrets.token_hex(32))"

    NOTE METHOD BELOW PRODUCES WEAKER KEYS AS IT DOES NOT USE HEX VALUES ABOVE
         7F
    NOTE Replace <32_char_string> with encryption key in ASCII format
    To convert to hex string to bytes, run following command in bash shell:
    python3 -c "print('<32_char_string>'.encode('ascii').hex())"
    '''
    key = bytes.fromhex(encryption_key)
    # key = encryption_key.encode('ascii')

    # New nonce everytime
    nonce = get_random_bytes(32)

    # Create cipher object
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Generate encrypted ciphertext
    ciphertext, tag = cipher.encrypt_and_digest(bytes_literal)

    return ciphertext, nonce, tag


def decrypt_string(ciphertext, encryption_key, nonce, tag):
    if ciphertext:
        try:
            cipher = AES.new(
                bytes.fromhex(encryption_key),
                AES.MODE_GCM,
                nonce=nonce
            )
            plaintext = cipher.decrypt_and_verify(
                ciphertext,
                tag
            ).decode('ascii')
        except Exception:
            traceback.print_exc()
            return ''
        else:
            return plaintext if isinstance(plaintext, str) else ''
    else:
        return None


def populate_necessary_rows():
    from maid.constants import MaidLanguageChoices, MaidResponsibilityChoices
    from maid.models import MaidLanguage, MaidResponsibility

    from .constants import AUTHORITY_GROUPS
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


def get_sg_region(post_code):
    from onlinemaid.sg_regions import SG_REGIONS

    if isinstance(post_code, str) and len(post_code) == 6:
        sector = SG_REGIONS.get(post_code[:2])
        return sector.get('region_code') if sector else None
    else:
        return None


def intervening_weekdays(start, end, inclusive=True, weekdays=[0, 1, 2, 3, 4]):
    # https://stackoverflow.com/a/43693117
    '''
    Function to calculate number of specified days of the week within date
    range
    weekdays mapping: MON==0, TUE==1, WED==2, THU==3, FRI==4, SAT==5, SUN==6
    '''
    if isinstance(start, datetime):
        start = start.date()               # make a date from a datetime

    if isinstance(end, datetime):
        end = end.date()                   # make a date from a datetime

    if end < start:
        # you can opt to return 0 or swap the dates around instead
        raise ValueError("start date must be before end date")

    if inclusive:
        end += timedelta(days=1)  # correct for inclusivity

    try:
        # collapse duplicate weekdays
        weekdays = {weekday % 7 for weekday in weekdays}
    except TypeError:
        weekdays = [weekdays % 7]

    ref = date.today()                    # choose a reference date
    ref -= timedelta(days=ref.weekday())  # and normalize its weekday

    # sum up all selected weekdays (max 7 iterations)
    # ref_p is ref_plus
    return sum(
        (ref_p - start).days // 7 - (ref_p - end).days // 7 for ref_p in (
            ref + timedelta(days=weekday) for weekday in weekdays
        )
    )


def humanise_time_duration(duration):
    if duration.days == 0 and duration.seconds >= 0 and duration.seconds < 60:
        if duration.seconds == 1:
            return str(duration.seconds) + " second"
        else:
            return str(duration.seconds) + " seconds"

    if (
        duration.days == 0
        and duration.seconds >= 60
        and duration.seconds < 3600
    ):
        minutes = math.floor(duration.seconds / 60)
        if minutes == 1:
            return str(minutes) + " minute"
        else:
            return str(minutes) + " minutes"

    if (
        duration.days == 0
        and duration.seconds >= 3600
        and duration.seconds < 86400
    ):
        hours = math.floor(duration.seconds / 3600)
        return str(hours) + " hour" if hours == 1 else str(hours) + " hours"

    if duration.days >= 1 and duration.days < 30:
        if duration.days == 1:
            return str(duration.days) + " day"
        else:
            return str(duration.days) + " days"

    if duration.days >= 30 and duration.days < 365:
        months = math.floor(duration.days / (365 / 12))
        if months == 1:
            return str(months) + " month"
        else:
            return str(months) + " months"

    if duration.days >= 365:
        years = math.floor(duration.days / 365)
        months = math.floor(duration.days % 365 / (365 / 12))
        if years == 1:
            years_str = str(years) + " year"
        else:
            years_str = str(years) + " years"
        if months == 1:
            months_str = str(months) + " month"
        else:
            months_str = str(months) + " months"
        return years_str + " and " + months_str if months else years_str


def maid_seed_data():
    import json

    from agency.models import Agency
    from maid.constants import (MaidCareRemarksChoices,
                                MaidGeneralHouseworkRemarksChoices,
                                MaidPassportStatusChoices, TypeOfMaidChoices)
    from maid.models import (Maid, MaidCooking, MaidDisabledCare,
                             MaidElderlyCare, MaidGeneralHousework,
                             MaidInfantChildCare, MaidLoanTransaction)
    maid_data = json.load(open('./maid.json'))

    # small_gif = (
    #     b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    #     b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    #     b'\x02\x4c\x01\x00\x3b'
    # )
    try:
        agency = Agency.objects.get(pk=1)
    except Agency.DoesNotExist:
        print('error')
    else:
        for maid in maid_data:
            try:
                Maid.objects.get(
                    reference_number=maid['reference_number'],
                )
            except Maid.DoesNotExist:
                encrption_thing = encrypt_string(
                    maid['passport_number'],
                    settings.ENCRYPTION_KEY
                )
                new_maid = Maid(
                    agency=agency,
                    reference_number=maid['reference_number'],
                    name=maid['name'],
                    passport_number=encrption_thing[0],
                    nonce=encrption_thing[1],
                    tag=encrption_thing[2],
                    maid_type=TypeOfMaidChoices.NEW,
                    days_off=maid['days_off'],
                    passport_status=MaidPassportStatusChoices.NOT_READY,
                    remarks=maid['remarks'],
                    published=True
                )
                new_maid.photo = 'maid.png'
                new_maid.save()
                MaidInfantChildCare.objects.create(
                    maid=new_maid,
                    assessment=random.randint(1, 5),
                    willingness=True,
                    experience=True,
                    remarks=MaidCareRemarksChoices.OWN_COUNTRY,
                    other_remarks=''
                )
                MaidElderlyCare.objects.create(
                    maid=new_maid,
                    assessment=random.randint(1, 5),
                    willingness=True,
                    experience=True,
                    remarks=MaidCareRemarksChoices.OWN_COUNTRY,
                    other_remarks=''
                )
                MaidDisabledCare.objects.create(
                    maid=new_maid,
                    assessment=random.randint(1, 5),
                    willingness=True,
                    experience=True,
                    remarks=MaidCareRemarksChoices.OWN_COUNTRY,
                    other_remarks=''
                )
                MaidGeneralHousework.objects.create(
                    maid=new_maid,
                    assessment=random.randint(1, 5),
                    willingness=True,
                    experience=True,
                    remarks=MaidGeneralHouseworkRemarksChoices.CAN_DO_ALL_HOUSEWORK,
                    other_remarks=''
                )
                MaidCooking.objects.create(
                    maid=new_maid,
                    assessment=random.randint(1, 5),
                    willingness=True,
                    experience=True,
                    remarks=MaidCareRemarksChoices.OWN_COUNTRY,
                    other_remarks=''
                )
                MaidLoanTransaction.objects.create(
                    maid=new_maid,
                    amount=100,
                    transaction_type='ADD',
                    description='this is a description',
                    transaction_date=date.today()
                )


def subscription_seed_data():
    import json

    from payment.models import SubscriptionProduct, SubscriptionProductPrice
    subscription_data = json.load(open('./subscriptions.json'))

    for subscription in subscription_data:
        sub_product, created = SubscriptionProduct.objects.get_or_create(
            id=subscription['subscription_product_id'],
            name=subscription['subscription_product_name'],
            description=subscription['subscription_product_description']
        )

        if created:
            for subscription_price in subscription['prices']:
                SubscriptionProductPrice.objects.get_or_create(
                    id=subscription_price['subcription_price_id'],
                    subscription_product=sub_product,
                    interval=subscription_price['subcription_price_interval'],
                    interval_count=subscription_price[
                        'subcription_price_interval_count'
                    ],
                    unit_amount=subscription_price[
                        'subcription_price_unit_amount'
                    ]
                )
