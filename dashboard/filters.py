# Imports from django
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
import django_filters

# Imports from local apps
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
    