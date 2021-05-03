# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## List Views
from .views import (
    DashboardMaidList, DashboardAccountList, DashboardAgencyPlanList,
    DashboardEnquiriesList, DashboardAgencyBranchList
)

## Detail Views
from .views import DashboardAgencyDetail, DashboardMaidDetail

## Form Views
from .views import DashboardMaidCreation, DashboardAgencyUpdate

## Create Views
from .views import DashboardAgencyEmployeeCreate

## Template Views
from .views import DashboardHomePage

## Update Views
from .views import (
    DashboardAgencyInformationUpdate, DashboardAgencyOpeningHoursUpdate,
    DashboardAgencyEmployeeUpdate
)

## Delete Views

## Generic Views
from .views import DashboardDataProviderView

# Start of Urls

urlpatterns = [
    path(
        'data/',
        DashboardDataProviderView.as_view(),
        name='dashboard_data_provider'
    ),
    path(
        'view/',
        include([
            path(
                'maids/',
                include([
                    path(
                        '',
                        DashboardMaidList.as_view(),
                        name='dashboard_maid_list'
                    ),
                    path(
                        '<int:pk>/',
                        DashboardMaidDetail.as_view(),
                        name='dashboard_maid_detail'
                    )
                ])
            ),
            path(
                'accounts',
                DashboardAccountList.as_view(),
                name='dashboard_account_list'
            ),
            path(
                'agency-details',
                DashboardAgencyDetail.as_view(),
                name='dashboard_agency_detail'
            ),
            path(
                'agency-plans',
                DashboardAgencyPlanList.as_view(),
                name='dashboard_agency_plan_list'
            ),
            path(
                'enquiries',
                DashboardEnquiriesList.as_view(),
                name='dashboard_enquiries_list'
            ),
            path(
                'branches',
                DashboardAgencyBranchList.as_view(),
                name='dashboard_branches_list'
            )
        ])
    ),
    path(
        'create/',
        include([
            path(
                'maid',
                DashboardMaidCreation.as_view(),
                name='dashboard_maid_creation'
            ),
            path(
                'employee',
                DashboardAgencyEmployeeCreate.as_view(),
                name='dashboard_employee_creation'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                'agency',
                DashboardAgencyUpdate.as_view(),
                name='dashboard_agency_update'
            ),
            path(
                'agency-information',
                DashboardAgencyInformationUpdate.as_view(),
                name='dashboard_agency_information_update'
            ),
            path(
                'agency-opening-hours',
                DashboardAgencyOpeningHoursUpdate.as_view(),
                name='dashboard_agency_opening_hours_update'
            ),
            path(
                'agency-employee/<int:pk>',
                DashboardAgencyEmployeeUpdate.as_view(),
                name='dashboard_agency_employee_update'
            )
        ])
    ),
    path(
        '',
        DashboardHomePage.as_view(),
        name='dashboard_home'
    )
]
