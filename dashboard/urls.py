# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## List Views
from .views import DashboardMaidList

## Detail Views

## Create Views

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
    path(
        '',
        DashboardMaidList.as_view(),
        name='dashboard_maid_list'
    )
]
