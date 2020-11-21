# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## List Views
from .views import (
    DashboardMaidList, DashboardAccountList, DashboardAgencyPlanList
)

## Detail Views
from .views import DashboardAgencyDetail

## Create Views

## Template Views
from .views import DashboardHomePage

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
    path(
        'view/',
        include([
            path(
                'maids',
                DashboardMaidList.as_view(),
                name='dashboard_maid_list'
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
            )
        ])
    ),
    path(
        '',
        DashboardHomePage.as_view(),
        name='dashboard_home'
    )
]
