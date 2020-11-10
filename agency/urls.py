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
    AgencyCreate, AgencyEmployeeCreate, AgencyPlanCreate, 
    AgencyAdministratorCreate
)

## Update Views
from .views import (
    AgencyUpdate, AgencyEmployeeUpdate,AgencyBranchUpdate, 
    AgencyOperatingHoursUpdate, AgencyPlanUpdate, AgencyAdministratorUpdate
)

## Delete Views
from .views import (
    AgencyDelete, AgencyEmployeeDelete, AgencyPlanDelete, 
    AgencyAdministratorDelete
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
                '<int:agency_id>',
                include([
                    path(
                        'admin/',
                        AgencyAdministratorCreate.as_view(),
                        name='agency_administrator_create'
                    ),
                    path(
                        'employee/',
                        AgencyEmployeeCreate.as_view(),
                        name='agency_employee_create'
                    )
                ])
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                '',
                AgencyDelete.as_view(),
                name='agency_delete'
            ),
            path(
                'administrator/<int:pk>',
                AgencyAdministratorDelete.as_view(),
                name='agency_administrator_delete'
            ),
            path(
                'employee/<int:pk>/',
                AgencyEmployeeDelete.as_view(),
                name='agency_employee_delete'
            ),
            path(
                'plan/<int:pk>/',
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
                'administrator/<int:pk>',
                AgencyAdministratorUpdate.as_view(),
                name='agency_administrator_update'
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
