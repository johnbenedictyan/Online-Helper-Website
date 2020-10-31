from django.utils.translation import ugettext_lazy as _

def TrueFalseChoices(TrueMessage, FalseMessage):
    return (
        ( True, _(TrueMessage) ),
        ( False, _(FalseMessage) )
    )
