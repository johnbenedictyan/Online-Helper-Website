# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Create Views
from .views import (
    MaidCreate
)

## Update Views
from .views import (
    MaidUpdate, MaidBiodataUpdate, MaidFamilyDetailsUpdate, 
    MaidInfantChildCareUpdate, MaidElderlyCareUpdate, MaidDisabledCareUpdate,
    MaidGeneralHouseworkUpdate,MaidCookingUpdate
)

## Delete Views
from .views import (
    MaidDelete
)

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                MaidCreate.as_view(),
                name='maid_create'
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                '<int:pk>/',
                MaidDelete.as_view(),
                name='maid_delete'
            ),
        ])
    ),
    path(
        'update/<int:pk>/',
        include([
            path(
                '',
                MaidUpdate.as_view(),
                name='maid_update'
            ),
            path(
                'biodata/',
                MaidBiodataUpdate.as_view(),
                name='maid_biodata_update'
            ),
            path(
                'family-details/',
                MaidFamilyDetailsUpdate.as_view(),
                name='maid_family_details_update'
            ),
            path(
                'icc/',
                MaidInfantChildCareUpdate.as_view(),
                name='maid_infant_child_care_update'
            ),
            path(
                'ec/',
                MaidElderlyCareUpdate.as_view(),
                name='maid_elderly_care_update'
            ),
            path(
                'dc/',
                MaidDisabledCareUpdate.as_view(),
                name='maid_disabled_care_update'
            ),
            path(
                'gh/',
                MaidGeneralHouseworkUpdate.as_view(),
                name='maid_general_housework_update'
            ),
            path(
                'c/',
                MaidCookingUpdate.as_view(),
                name='maid_cooking_update'
            )
        ])
    )
]
