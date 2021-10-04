import re


from django.utils.translation import ugettext_lazy as _

# Start of Validators


def validate_nric(test_id):
    # return error message if fail, else return None for success
    test_id = test_id.upper() if isinstance(test_id, str) else ''
    error_msg = f'{test_id} is not a valid NRIC'

    if not re.match('^[ST][0-9]{7}[ABCDEFGHIZJ]$', test_id):
        return _(error_msg)
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
        return None if checksum_chr == test_id[-1] else _(error_msg)


def validate_fin(test_id):
    # return error message if fail, else return None for success
    test_id = test_id.upper() if isinstance(test_id, str) else ''
    error_msg = f'{test_id} is not a valid FIN'

    if not re.match('^[FG][0-9]{7}[KLMNPQRTUWX]$', test_id):
        return _(error_msg)
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
        return None if checksum_chr == test_id[-1] else _(error_msg)


def validate_passport(plaintext):
    # return error message if fail, else return None for success
    if not isinstance(plaintext, str):
        return _('Must be a string')
    if len(plaintext) > 20:
        return _('Passport must not exceed 20 characters')
    if not re.match('^[A-Za-z0-9]*$', plaintext):
        return _('Can only enter letters or numbers')
    return None


def validate_ea_personnel_number(ea_personnel_number):
    # return error message if fail, else return None for success
    if not isinstance(ea_personnel_number, str):
        return _('Must be a string')
    if ea_personnel_number == 'NA':
        return _(
            'Assigned agent must have a valid EA personnel registration number'
        )
    if not re.match('^R[0-9]{7}$', ea_personnel_number.upper()):
        return _(
            f'''{ea_personnel_number}" is not a valid EA Personnel Registration
            Number'''
        )
    return None
