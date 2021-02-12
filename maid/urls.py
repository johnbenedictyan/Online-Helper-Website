# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Form Views
from .views import MaidCreateFormView

## Redirect Views
from .views import MaidTogglePublished

## List Views
from .views import MaidList

## Detail Views
from .views import MaidDetail

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

## Generic Views
from .views import MaidProfileView

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                MaidCreateFormView.as_view(),
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
    ),
    path(
        'view/',
        include([
            path(
                '',
                MaidList.as_view(),
                name='maid_list'
            ),
            path(
                '<int:pk>/',
                include([
                    path(
                        '',
                        MaidDetail.as_view(),
                        name='maid_detail'
                    ),
                    path(
                        'profile/',
                        MaidProfileView.as_view(),
                        name='maid_profile'
                    )
                ])
            )
        ])
    ),
    path(
        'togglepublished/<int:pk>/',
        MaidTogglePublished.as_view(),
        name='maid_toggle_published'
    )
]
