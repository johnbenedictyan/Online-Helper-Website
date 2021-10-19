import re
from typing import NoReturn, Union

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from onlinemaid.helper_functions import is_of_age, is_pasted

# Start of Validators


def validate_passport_date(dt) -> Union[NoReturn, None]:
    if is_pasted(dt):
        error_msg = _('This passport is expired')
        raise ValidationError(error_msg)


def validate_age(dt, age) -> Union[NoReturn, None]:
    if not is_of_age(dt, age):
        error_msg = f'This individual is not at least {age} years old'
        raise ValidationError(error_msg)


def validate_nric(test_id) -> Union[NoReturn, None]:
    if not test_id:
        empty_nric = _("NRIC cannot be empty")
        raise ValidationError(empty_nric)

    # return error message if fail, else return None for success
    test_id = test_id.upper() if isinstance(test_id, str) else ''
    error_msg = f'{test_id} is not a valid NRIC'

    if not re.match('^[ST][0-9]{7}[ABCDEFGHIZJ]$', test_id):
        raise ValidationError(error_msg)
    else:
        WEIGHTS = [2, 7, 6, 5, 4, 3, 2]
        CHECK_MAP_ST = {
            1: 'A',
            2: 'B',
            3: 'C',
            4: 'D',
            5: 'E',
            6: 'F',
            7: 'G',
            8: 'H',
            9: 'I',
            10: 'Z',
            11: 'J',
        }
        total = 0

        for i, (c, w) in enumerate(zip(test_id[1:8], WEIGHTS)):
            c = int(ord(c) - 48)
            check_weight = c * w
            total += check_weight

        total += 4 if test_id[0] == 'T' else 0
        checksum_num = 11 - (total % 11)
        checksum_chr = CHECK_MAP_ST.get(checksum_num)
        if checksum_chr != test_id[-1]:
            raise ValidationError(error_msg)


def validate_fin(test_id) -> Union[NoReturn, None]:
    if not test_id:
        empty_fin = _("FIN cannot be empty")
        raise ValidationError(empty_fin)

    # return error message if fail, else return None for success
    test_id = test_id.upper() if isinstance(test_id, str) else ''
    error_msg = f'{test_id} is not a valid FIN'

    if not re.match('^[FG][0-9]{7}[KLMNPQRTUWX]$', test_id):
        raise ValidationError(error_msg)
    else:
        WEIGHTS = [2, 7, 6, 5, 4, 3, 2]
        CHECK_MAP_FG = {
            1: 'K',
            2: 'L',
            3: 'M',
            4: 'N',
            5: 'P',
            6: 'Q',
            7: 'R',
            8: 'T',
            9: 'U',
            10: 'W',
            11: 'X',
        }
        total = 0

        for i, (c, w) in enumerate(zip(test_id[1:8], WEIGHTS)):
            c = int(ord(c) - 48)
            check_weight = c * w
            total += check_weight

        total += 4 if test_id[0] == 'G' else 0
        checksum_num = 11 - (total % 11)
        checksum_chr = CHECK_MAP_FG.get(checksum_num)
        if checksum_chr != test_id[-1]:
            raise ValidationError(error_msg)


def validate_passport(passport_text) -> Union[NoReturn, None]:
    if not passport_text:
        error_msg = _("Passport number cannot be empty")
        raise ValidationError(error_msg)

    # return error message if fail, else return None for success
    if not isinstance(passport_text, str):
        error_msg = _('Must be a string')
        raise ValidationError(error_msg)
    if len(passport_text) > 20:
        error_msg = _('Passport must not exceed 20 characters')
        raise ValidationError(error_msg)
    if not re.match('^[A-Za-z0-9]*$', passport_text):
        error_msg = _('Can only enter letters or numbers')
        raise ValidationError(error_msg)


def validate_ea_personnel_number(ea_personnel_number) -> Union[NoReturn, None]:
    error_msg = None
    if not ea_personnel_number:
        error_msg = _("EA Personnel number cannot be empty")

    # return error message if fail, else return None for success
    if not isinstance(ea_personnel_number, str):
        error_msg = _('Must be a string')
    if ea_personnel_number == 'NA':
        error_msg = _(
            'Assigned agent must have a valid EA personnel registration number'
        )
    if not re.match('^R[0-9]{7}$', ea_personnel_number.upper()):
        error_msg = _(
            f'''{ea_personnel_number}" is not a valid EA Personnel Registration
            Number'''
        )
    if error_msg:
        raise ValidationError(error_msg)
