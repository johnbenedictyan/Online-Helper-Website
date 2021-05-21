# Imports from django
import django
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
import django_filters

# Imports from local apps
from employer_documentation.models import Employer
from maid.models import Maid

# Start of Filters
class DashboardMaidFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Search By'),
        widget=TextInput(attrs={'placeholder': 'FDW Name'})
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        lookup_expr='exact',
        label=_('Filter By'),
        empty_label=_('Any')
    )
    class Meta:
        model = Maid
        fields = [
            'name',
            'status'
        ]

class DashboardEmployerFilter(django_filters.FilterSet):
    employer_name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Search By'),
        widget=TextInput(attrs={'placeholder': 'Name or Mobile'})
    )
    agency_employee = django_filters.ChoiceFilter(
        field_name='status',
        lookup_expr='exact',
        label=_('Filter By EA Personnel'),
        empty_label=_('Any')
    )
    class Meta:
        model = Employer
        fields = [
            'employer_name',
            'agency_employee'
        ]

class DashboardCaseFilter(django_filters.FilterSet):
    pass

class DashboardSalesFilter(django_filters.FilterSet):
    pass

class DashboardStatusFilter(django_filters.FilterSet):
    pass