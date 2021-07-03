# Python
from datetime import timedelta

# Imports from django
from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
import django_filters

from onlinemaid.constants import MaritalStatusChoices
# Imports from local apps
from .constants import TypeOfMaidChoices, MaidCountryOfOrigin, MaidCreatedOnChoices
from .models import Maid, MaidResponsibility, MaidLanguage
from .widgets import CustomRangeWidget
from agency.models import Agency

# Start of Filters
class MiniMaidFilter(django_filters.FilterSet):
    country_of_origin = django_filters.ChoiceFilter(
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
            'country_of_origin': ['exact'],
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
        label=_('Search by Maid Name')
    )
    languages = django_filters.ModelMultipleChoiceFilter(
        field_name='languages',
        lookup_expr='exact',
        queryset=MaidLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label=_('Language Spoken')
    )
    country_of_origin = django_filters.ChoiceFilter(
        field_name='country_of_origin',
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
        field_name='marital_status',
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
    created_on = django_filters.ChoiceFilter(
        field_name='created_on',
        label=_('Created On'),
        choices=MaidCreatedOnChoices.choices,
        empty_label=_('No Preference'),
        method='created_on_filter'
    )
    agency = django_filters.ModelChoiceFilter(
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
            365*int(value.stop+1)+int(value.stop//4)
        )
        end_date = time_now - timedelta(
            365*int(value.start)+int(value.start//4)
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
        