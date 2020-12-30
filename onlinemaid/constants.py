from django.utils.translation import ugettext_lazy as _

# Agency user groups
AG_OWNERS = 'Agency Owners'
AG_ADMINS = 'Agency Administrators'
AG_MANAGERS = 'Agency Managers'
AG_SALES = 'Agency Sales Staff'

def TrueFalseChoices(TrueMessage, FalseMessage):
    return (
        ( True, _(TrueMessage) ),
        ( False, _(FalseMessage) )
    )
