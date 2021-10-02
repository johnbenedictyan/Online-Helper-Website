from agency.models import AgencyEmployee
from django.db.models import Q
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _
from django_filters import CharFilter as DjangoFiltersCharFilter
from django_filters import ChoiceFilter as DjangoFiltersChoiceFilter
from django_filters import FilterSet as DjangoFiltersFilterSet
from django_filters import ModelChoiceFilter as DjangoFilterModelChoiceFilter
from employer_documentation.models import CaseStatus, Employer, EmployerDoc
from maid.constants import MaidStatusChoices
from maid.models import Maid
from onlinemaid.constants import AG_MANAGERS, AG_SALES

# Start of Filters


class DashboardMaidFilter(DjangoFiltersFilterSet):
    name = DjangoFiltersCharFilter(
        field_name='name',
        lookup_expr='icontains',
        label=_('Search By'),
        widget=TextInput(attrs={'placeholder': 'FDW Name'})
    )
    status = DjangoFiltersChoiceFilter(
        field_name='status',
        lookup_expr='exact',
        label=_('Filter By'),
        choices=MaidStatusChoices.choices,
        empty_label=_('Any')
    )

    class Meta:
        model = Maid
        fields = [
            'name',
            'status'
        ]


def get_agency_employee_list(requestObj):
    agency_id = requestObj['agency_id']
    authority = requestObj['authority']
    user = requestObj['user']
    qs = AgencyEmployee.objects.filter(
        agency__pk=agency_id
    )

    if authority == AG_MANAGERS:
        qs = qs.filter(
            branch=user.agency_employee.branch
        )
    elif authority == AG_SALES:
        qs = qs.filter(
            user=user
        )
    return qs


class DashboardEmployerFilter(DjangoFiltersFilterSet):
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

    employer_name = DjangoFiltersCharFilter(
        field_name='employer_name',
        lookup_expr='icontains',
        label=_('Search By'),
        widget=TextInput(attrs={'placeholder': 'Name or Mobile'})
    )

    # agency_employee = DjangoFilterModelChoiceFilter(
    #     field_name='agency_employee',
    #     lookup_expr='exact',
    #     label=_('Filter By EA Personnel'),
    #     queryset=get_agency_employee_list,
    #     method='agency_employee_filter',
    #     empty_label=_('Any')
    # )

    employer_birthday_month = DjangoFiltersChoiceFilter(
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

    def agency_employee_filter(self, queryset, name, value):
        return queryset


class DashboardCaseFilter(DjangoFiltersFilterSet):
    employer_fdw_search = DjangoFiltersCharFilter(
        label='Search By',
        method='custom_employer_fdw_filter',
        widget=TextInput(
            attrs={
                'placeholder': 'Employer / FDW'
            }
        )
    )

    agency_employee = DjangoFilterModelChoiceFilter(
        field_name='agency_employee',
        lookup_expr='exact',
        label=_('Filter By EA Personnel'),
        queryset=get_agency_employee_list,
        method='agency_employee_filter',
        empty_label=_('Any')
    )

    class Meta:
        model = EmployerDoc
        fields = [
            'employer__employer_name',
            'fdw__name',
            'employer__agency_employee'
        ]

    def custom_employer_fdw_filter(self, queryset, name, value):
        return queryset.filter(
            Q(employer__employer_name__icontains=value) |
            Q(fdw__name__icontains=value)
        )

    def agency_employee_filter(self, queryset, name, value):
        return queryset


class DashboardSalesFilter(DjangoFiltersFilterSet):
    employer_fdw_search = DjangoFiltersCharFilter(
        label='Search By',
        method='custom_employer_fdw_filter',
        widget=TextInput(
            attrs={
                'placeholder': 'Employer / FDW'
            }
        )
    )

    class Meta:
        model = EmployerDoc
        fields = [
            'employer__employer_name',
            'fdw__name'
        ]

    def custom_employer_fdw_filter(self, queryset, name, value):
        return queryset.filter(
            Q(employer__employer_name__icontains=value) |
            Q(fdw__name__icontains=value)
        )


class DashboardStatusFilter(DjangoFiltersFilterSet):
    employer_fdw_search = DjangoFiltersCharFilter(
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
