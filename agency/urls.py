# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app
# from .forms import (
    
# )

# Create Views
from .views import (
    AgencyCreate, AgencyEmployeeCreate, AgencyPlanCreate,
)

# Update Views
from .views import (
    AgencyUpdate, AgencyContactInformationUpdate, AgencyEmployeeUpdate,
    AgencyLocationUpdate, AgencyOperatingHoursUpdate, AgencyPlanUpdate
)

# Delete Views
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
                'employee/',
                AgencyEmployeeCreate.as_view(),
                name='agency_employee_create'
            ),
            path(
                'plan/',
                AgencyPlanCreate.as_view(),
                name='agency_plan_create'
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
                'employee/',
                AgencyEmployeeDelete.as_view(),
                name='agency_employee_delete'
            ),
            path(
                'plan/',
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
                'contact-information/',
                AgencyContactInformationUpdate.as_view(),
                name='agency_contact_information_update'
            ),
            path(
                'employee/',
                AgencyEmployeeUpdate.as_view(),
                name='agency_employee_update'
            ),
            path(
                'location/',
                AgencyLocationUpdate.as_view(),
                name='agency_location_update'
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
    )
]
