from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='faee', is_safe=True)
@stringfilter
def format_agency_employee_email(value):
    if value.split('@')[1] == settings.AGENCY_EMPLOYEE_FEP:
        return ''


# @register.filter(name='enquirymaidfilter', is_safe=True)
# def get_maids(value, agency_id):
#     return value.filter(
#         agency__pk=agency_id
#     )


@register.filter(name='enquiryimfilter', is_safe=True)
def get_im(value, agency_id):
    return value.filter(
        maid__agency__pk=agency_id
    )


@register.filter
def keyvalue(dict, key):
    return dict[key]


@register.simple_tag
def define(val=None):
    return val
