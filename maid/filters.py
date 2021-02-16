# Imports from django
from django import forms
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
import django_filters

# Imports from local apps
from .constants import (
    TypeOfMaidChoices, MaidCountryOfOrigin, MaritalStatusChoices
)
from .models import Maid, MaidResponsibility, MaidLanguage

# Start of Filters
class MiniMaidFilter(django_filters.FilterSet):
    personal_details__country_of_origin = django_filters.ChoiceFilter(
        choices = MaidCountryOfOrigin.choices,
        empty_label = _('Any'),
        label=''
    )
    maid_type = django_filters.ChoiceFilter(
        choices = TypeOfMaidChoices.choices,
        empty_label = _('Any'),
        label=''
    )
    responsibilities = django_filters.ModelChoiceFilter(
        queryset=MaidResponsibility.objects.all(),
        empty_label = _('Any'),
        label=''
    )
    
    class Meta:
        model = Maid
        fields = {
            'personal_details__country_of_origin': ['exact'],
            'maid_type': ['exact'],
            'responsibilities': ['exact']
        }
        
class MaidFilter(django_filters.FilterSet):
    # TODO: Add main responsibility and language ability
    personal_details__languages = django_filters.ModelMultipleChoiceFilter(
        queryset=MaidLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Language Spoken'
    )
    personal_details__country_of_origin = django_filters.ChoiceFilter(
        choices = MaidCountryOfOrigin.choices,
        empty_label = _('Any')
    )
    maid_type = django_filters.ChoiceFilter(
        choices = TypeOfMaidChoices.choices,
        empty_label = _('Any')
    )
    family_details__marital_status = django_filters.ChoiceFilter(
        choices = MaritalStatusChoices.choices,
        empty_label = _('Any')
    )
    responsibilities = django_filters.ModelMultipleChoiceFilter(
        queryset=MaidResponsibility.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Maid Responsibilites'
    )

    class Meta:
        model = Maid
        fields = {
            'personal_details__country_of_origin': ['exact'],
            'maid_type': ['exact'],
            'personal_details__age': ['lt', 'gt'],
            'family_details__marital_status': ['exact'],
            'responsibilities': ['exact'],
            'personal_details__languages': ['exact']
        }
