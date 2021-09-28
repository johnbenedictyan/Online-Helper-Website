# Django Imports
from django.urls import include, path

# App Imports
from .views import (
    AgencySignUp, AgencyList, AgencyDetail, AgencyCreate, AgencyOwnerCreate,
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
                'employee/<int:pk>/',
                AgencyEmployeeDelete.as_view(),
                name='agency_employee_delete'
            ),
            path(
                'plan/<int:pk>/',
                AgencyPlanDelete.as_view(),
                name='agency_plan_delete'
            ),
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
                '<slug:pk>/',
                AgencyDetail.as_view(),
                name='agency_detail'
            )
        ])
    ),
    path(
        'sign-up/',
        AgencySignUp.as_view(),
        name='agency_sign_up'
    )
]
