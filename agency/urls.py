# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

# Form Views
from .views import AgencySignUp

# List Views
from .views import AgencyList

# Detail Views
from .views import AgencyDetail

# Create Views
from .views import AgencyCreate, AgencyOwnerCreate

# Update Views

# Delete Views
from .views import AgencyDelete, AgencyEmployeeDelete, AgencyPlanDelete

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
                '<int:pk>/',
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
