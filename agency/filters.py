from django.db.models import Q
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter as DjangoFiltersCharFilter
from django_filters import ChoiceFilter as DjangoFiltersChoiceFilter
from django_filters import FilterSet as DjangoFiltersFilterSet

from .constants import AreaChoices
from .models import Agency

# Start of Filters


class AgencyFilter(DjangoFiltersFilterSet):
    name = DjangoFiltersCharFilter(
        label='Search',
        method='custom_agency_filter',
        widget=TextInput(attrs={'placeholder': 'Agency, address, tel...'})
    )
    branches__area = DjangoFiltersChoiceFilter(
        label=_('Location'),
        choices=AreaChoices.choices,
        empty_label=_('Any')
    )

    class Meta:
        model = Agency
        fields = {
            'name': ['exact'],
            'branches__area': ['exact'],
        }

    def custom_agency_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(branches__address_1__icontains=value) |
            Q(branches__address_2__icontains=value) |
            Q(branches__postal_code__icontains=value) |
            Q(branches__office_number__icontains=value) |
            Q(branches__mobile_number__icontains=value)
        )
