from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_postcode(value):
    err_msg = _('%(value)s is not a valid Singapore post code')
    if len(value)!= 6:
        raise ValidationError(
            err_msg,
            params={'value': value},
        )
