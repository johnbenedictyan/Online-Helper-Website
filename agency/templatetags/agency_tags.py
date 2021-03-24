from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@stringfilter
def format_contact_number(value):
    l = len(value)//2
    return value[:l] + ' ' +value[l:]

register.filter('fcn', format_contact_number)