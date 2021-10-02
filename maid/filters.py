# Global Imports
from datetime import timedelta

# Project Apps Imports
from agency.models import Agency
# Django Imports
from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
# Foreign Apps Imports
from django_filters import (CharFilter, ChoiceFilter, FilterSet,
                            ModelChoiceFilter, ModelMultipleChoiceFilter,
                            RangeFilter)
from onlinemaid.constants import MaritalStatusChoices

# App Imports
from .constants import (MaidCountryOfOrigin, MaidCreatedOnChoices,
                        TypeOfMaidChoices)
from .models import Maid, MaidLanguage, MaidResponsibility
from .widgets import CustomRangeWidget

# Start of Filters


class MiniMaidFilter(FilterSet):
    country_of_origin = ChoiceFilter(
        choices=MaidCountryOfOrigin.choices,
        empty_label=_('No Preference'),
        label=''
    )
    maid_type = ChoiceFilter(
        choices=TypeOfMaidChoices.choices,
        empty_label=_('No Preference'),
        label=''
    )
    responsibilities = ModelChoiceFilter(
        queryset=MaidResponsibility.objects.all(),
        empty_label=_('No Preference'),
        label=''
    )

    class Meta:
        model = Maid
        fields = {
            'country_of_origin': ['exact'],
            'maid_type': ['exact'],
            'responsibilities': ['exact']
        }


class MaidFilter(FilterSet):
    def filter_age_between(self, queryset, name, value):
        # gt and min value and lt max value
        print(value)
        return queryset

    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Search by Maid Name')
    )
    languages = ModelMultipleChoiceFilter(
        field_name='languages',
        lookup_expr='exact',
        queryset=MaidLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=_('Language Spoken')
    )
    country_of_origin = ChoiceFilter(
        field_name='country_of_origin',
        lookup_expr='exact',
        label=_('Country of Origin'),
        choices=MaidCountryOfOrigin.choices,
        empty_label=_('No Preference')
    )
    maid_type = ChoiceFilter(
        label=_('Type of Maid'),
        choices=TypeOfMaidChoices.choices,
        empty_label=_('No Preference')
    )
    marital_status = ChoiceFilter(
        field_name='marital_status',
        lookup_expr='exact',
        label=_('Marital Status'),
        choices=MaritalStatusChoices.choices,
        empty_label=_('No Preference')
    )
    responsibilities = ModelMultipleChoiceFilter(
        queryset=MaidResponsibility.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=_('Maid Responsibilites')
    )
    age = RangeFilter(
        label=_('Age'),
        method='custom_age_filter',
        widget=CustomRangeWidget(
            attrs={
                'hidden': True
            }
        )
    )
    created_on = ChoiceFilter(
        field_name='created_on',
        label=_('Added In'),
        choices=MaidCreatedOnChoices.choices,
        empty_label=_('No Preference'),
        method='created_on_filter'
    )
    agency = ModelChoiceFilter(
        label=_('Agency'),
        queryset=Agency.objects.all(),
        empty_label=_('No Preference')
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
            'responsibilities',
            'created_on'
        ]

    def custom_age_filter(self, queryset, name, value):
        time_now = timezone.now()
        start_date = time_now - timedelta(
            365 * int(value.stop + 1) + int(value.stop // 4)
        )
        end_date = time_now - timedelta(
            365 * int(value.start) + int(value.start // 4)
        )
        return queryset.filter(
            date_of_birth__range=(
                start_date,
                end_date
            )
        )

    def created_on_filter(self, queryset, name, value):
        if value:
            time_now = timezone.now()
            queryset = queryset.filter(
                created_on__gt=time_now - timedelta(days=int(value))
            )
        return queryset
