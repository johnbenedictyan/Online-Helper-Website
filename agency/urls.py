# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## List Views
from .views import AgencyList

## Detail Views
from .views import AgencyDetail

## Create Views
from .views import (
    AgencyCreate, AgencyEmployeeCreate, AgencyPlanCreate, AgencyOwnerCreate
)

## Update Views
from .views import (
    AgencyUpdate, AgencyEmployeeUpdate,AgencyBranchUpdate, AgencyPlanUpdate,
    AgencyOperatingHoursUpdate
)

## Delete Views
from .views import (
    AgencyDelete, AgencyEmployeeDelete, AgencyPlanDelete
)

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                AgencyCreate.as_view(),
                name='agency_create'
            ),
            path(
                'plan/',
                AgencyPlanCreate.as_view(),
                name='agency_plan_create'
            ),
            path(
                'employee/',
                AgencyEmployeeCreate.as_view(),
                name='agency_employee_create'
            ),
            path(
                '<int:pk>/owner/',
                AgencyOwnerCreate.as_view(),
                name='agency_owner_create'
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                '<int:pk>/',
                AgencyDelete.as_view(),
                name='agency_delete'
            ),
            path(
                '<int:pk>/employee/',
                AgencyEmployeeDelete.as_view(),
                name='agency_employee_delete'
            ),
            path(
                '<int:pk>/plan/',
                AgencyPlanDelete.as_view(),
                name='agency_plan_delete'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                '',
                AgencyUpdate.as_view(),
                name='agency_update'
            ),
            path(
                'employee/<int:pk>',
                AgencyEmployeeUpdate.as_view(),
                name='agency_employee_update'
            ),
            path(
                'branch/<int:pk>',
                AgencyBranchUpdate.as_view(),
                name='agency_branch_update'
            ),
            path(
                'operating-hours/',
                AgencyOperatingHoursUpdate.as_view(),
                name='agency_operating_hours_update'
            ),
            path(
                'plan/',
                AgencyPlanUpdate.as_view(),
                name='agency_plan_update'
            )
        ])
    ),
    path(
        'view/',
        include([
            path(
                '',
                AgencyList.as_view(),
                name='agency_list'
            ),
            path(
                '<int:pk>/',
                AgencyDetail.as_view(),
                name='agency_detail'
            )
        ])
    )
]
