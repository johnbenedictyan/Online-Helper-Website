from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@stringfilter
def format_contact_number(value):
    l = len(value)//2
    return value[:l] + ' ' +value[l:]

@stringfilter
def format_branch_name(value):
    if not 'branch' in value:
        return value + 'Branch'

register.filter('fcn', format_contact_number)
register.filter('fbn', format_branch_name) 