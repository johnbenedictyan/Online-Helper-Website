# Imports from django

# Imports from foreign installed apps
import django_filters

# Imports from local apps
from .models import Maid

# Start of Filters
class MaidFilter(django_filters.FilterSet):
    # TODO: Add main responsibility and language ability
    class Meta:
        model = Maid
        fields = {
            'biodata__country_of_origin': ['exact'],
            'maid_type': ['exact'],
            'biodata__age': ['lt', 'gt'],
            'family_details__marital_status': ['exact']
        }
