from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='faee', is_safe=True)
@stringfilter
def format_agency_employee_email(value):
    if value.split('@')[1] == settings.AGENCY_EMPLOYEE_FEP:
        return ''
