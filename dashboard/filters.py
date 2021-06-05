# Imports from django
from django.db.models import Q, fields
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
import django_filters

# Imports from local apps
from employer_documentation.models import Employer, CaseStatus
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
    MONTH_CHOICES = (
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December')
    )

    employer_name = django_filters.CharFilter(
        field_name='employer_name',
        lookup_expr='icontains',
        label=_('Search By'),
        widget=TextInput(attrs={'placeholder': 'Name or Mobile'})
    )

    agency_employee = django_filters.ChoiceFilter(
        field_name='agency_employee',
        lookup_expr='exact',
        label=_('Filter By EA Personnel'),
        empty_label=_('Any')
    )

    employer_birthday_month = django_filters.ChoiceFilter(
        field_name='employer_date_of_birth',
        choices=MONTH_CHOICES,
        method='employer_birthday_month_filter',
        label=_('Filter By Birthday Month'),
        empty_label=_('Any')
    )

    class Meta:
        model = Employer
        fields = [
            'employer_name',
            'agency_employee'
        ]

    def employer_birthday_month_filter(self, queryset, name, value):
        return queryset.filter(
            employer_date_of_birth__month=value
        )

class DashboardCaseFilter(django_filters.FilterSet):
    pass

class DashboardSalesFilter(django_filters.FilterSet):
    pass

class DashboardStatusFilter(django_filters.FilterSet):
    employer_fdw_search = django_filters.CharFilter(
        label='Search By',
        method='custom_employer_fdw_filter',
        widget=TextInput(
            attrs={
                'placeholder': 'Employer / FDW'
            }
        )
    )
    class Meta:
        model = CaseStatus
        fields = [
            'employer_doc'
        ]

    def custom_employer_fdw_filter(self, queryset, name, value):
        return queryset.filter(
            Q(employer_doc__employer__employer_name__icontains=value) |
            Q(employer_doc__fdw__name__icontains=value)
        )