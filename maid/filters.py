# Python
from datetime import timedelta

# Imports from django
from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
import django_filters

# Imports from local apps
from .constants import (
    TypeOfMaidChoices, MaidCountryOfOrigin, MaritalStatusChoices
)
from .models import Maid, MaidResponsibility, MaidLanguage
from .widgets import CustomRangeWidget

# Start of Filters
class MiniMaidFilter(django_filters.FilterSet):
    personal_details__country_of_origin = django_filters.ChoiceFilter(
        choices=MaidCountryOfOrigin.choices,
        empty_label=_('No Preference'),
        label=''
    )
    maid_type = django_filters.ChoiceFilter(
        choices=TypeOfMaidChoices.choices,
        empty_label=_('No Preference'),
        label=''
    )
    responsibilities = django_filters.ModelChoiceFilter(
        queryset=MaidResponsibility.objects.all(),
        empty_label=_('No Preference'),
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
    def filter_age_between(self, queryset, name, value):
        # gt and min value and lt max value
        print(value)
        return queryset
        
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Name')
    )
    languages = django_filters.ModelMultipleChoiceFilter(
        field_name='personal_details__languages',
        lookup_expr='exact',
        queryset=MaidLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=_('Language Spoken')
    )
    country_of_origin = django_filters.ChoiceFilter(
        field_name='personal_details__country_of_origin',
        lookup_expr='exact',
        label=_('Country of Origin'),
        choices=MaidCountryOfOrigin.choices,
        empty_label=_('No Preference')
    )
    maid_type = django_filters.ChoiceFilter(
        label=_('Type of Maid'),
        choices=TypeOfMaidChoices.choices,
        empty_label=_('No Preference')
    )
    marital_status = django_filters.ChoiceFilter(
        field_name='family_details__marital_status',
        lookup_expr='exact',
        label=_('Marital Status'),
        choices=MaritalStatusChoices.choices,
        empty_label=_('No Preference')
    )
    responsibilities = django_filters.ModelMultipleChoiceFilter(
        queryset=MaidResponsibility.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=_('Maid Responsibilites')
    )
    age = django_filters.RangeFilter(
        label=_('Age'),
        method='custom_age_filter',
        widget=CustomRangeWidget(
            attrs={
                'hidden': True
            }
        )
    )

    class Meta:
        model = Maid
        fields = [
            'name',
            'maid_type',
            'country_of_origin',
            'age',
            'marital_status',
            'languages',
            'responsibilities'
        ]

    def custom_age_filter(self, queryset, name, value):
        time_now = timezone.now()
        start_date = time_now - timedelta(
            365*int(value.stop)+int(value.stop//4)
        )
        end_date = time_now - timedelta(
            365*int(value.start)+int(value.start//4)
        )
        return queryset.filter(
            personal_details__date_of_birth__range=(
                start_date,
                end_date
            )
        )
