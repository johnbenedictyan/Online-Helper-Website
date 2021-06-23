from django.utils.translation import ugettext_lazy as _

# Agency user groups
AG_OWNERS = 'Agency Owners'
AG_ADMINS = 'Agency Administrators'
AG_MANAGERS = 'Agency Managers'
AG_SALES = 'Agency Sales Staff'
AG_ADMIN_STAFF = 'Agency Admin Staff'
P_EMPLOYERS = 'Potential Employers'
AUTHORITY_GROUPS = [
    AG_OWNERS,
    AG_ADMINS,
    AG_MANAGERS,
    AG_SALES,
    AG_ADMIN_STAFF,
    P_EMPLOYERS
]

def TrueFalseChoices(TrueMessage, FalseMessage):
    return (
        ( True, _(TrueMessage) ),
        ( False, _(FalseMessage) )
    )
