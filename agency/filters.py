# Imports from django
from django import forms
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
import django_filters

# Imports from local apps
from .constants import AreaChoices
from .models import Agency

# Start of Filters
class AgencyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    branches__area = django_filters.ChoiceFilter(
        label = _('Location'),
        choices = AreaChoices.choices,
        empty_label = _('Any')
    )

    class Meta:
        model = Agency
        fields = {
            'name': ['exact'],
            'branches__area': ['exact'],
        }
