import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# from profanity_check import predict

# def validate_obscene_language(value):
#     if predict([value] == 1):
#         raise ValidationError(
#             _('%(value)s contains obscene language'),
#             params={'value': value},
#         )

def validate_links(value):
    url_regex = "(?P<url>https?://[^\s]+)"
    try:
        re.search(url_regex, value).group('url')
    except:
        return value
    else:
        raise ValidationError(
            _('%(value)s contains links'),
            params={'value': value},
        )