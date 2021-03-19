# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Form Views
from .views import MaidCreateFormView, MaidCareDetailsUpdate

## Redirect Views
from .views import MaidTogglePublished, MaidToggleFeatured

## List Views
from .views import MaidList

## Detail Views
from .views import MaidDetail, PdfMaidBiodataView

## Create Views
from .views import (
    MaidCreate, MaidEmploymentHistoryCreate
)

## Update Views
from .views import (
    MaidUpdate, MaidPersonalDetailsUpdate, MaidFamilyDetailsUpdate, 
    MaidInfantChildCareUpdate, MaidElderlyCareUpdate, MaidDisabledCareUpdate,
    MaidGeneralHouseworkUpdate, MaidCookingUpdate, MaidFinancialDetailsUpdate,
    MaidAgencyFeeTransactionUpdate
)

## Delete Views
from .views import (
    MaidDelete
)

## Generic Views
from .views import MaidProfileView, FeaturedMaidListView

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                MaidCreateFormView.as_view(),
                name='maid_create'
            ),
            path(
                'employment/',
                MaidEmploymentHistoryCreate.as_view(),
                name='maid_employment_create'
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
                MaidPersonalDetailsUpdate.as_view(),
                name='maid_personal_details_update'
            ),
            path(
                'family-details/',
                MaidFamilyDetailsUpdate.as_view(),
                name='maid_family_details_update'
            ),
            path(
                'finance/',
                MaidFinancialDetailsUpdate.as_view(),
                name='maid_financial_details_update'
            ),
            path(
                'care/',
                MaidCareDetailsUpdate.as_view(),
                name='maid_care_details_update'
            ),
            path(
                'aft/<int:agency_fee_transaction_pk>/',
                MaidAgencyFeeTransactionUpdate.as_view(),
                name='maid_agency_fee_transaction_update'
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
                'featured/',
                FeaturedMaidListView.as_view(),
                name='featured_maid_list'
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
                    ),
                    path(
                        'biodata/pdf/',
                        PdfMaidBiodataView.as_view(),
                        name='maid_biodata_pdf'
                    ),
                ])
            )
        ])
    ),
    path(
        'toggle/<int:pk>/',
        include([
            path(
                'published',
                MaidTogglePublished.as_view(),
                name='maid_toggle_published'
            ),
            path(
                'featured',
                MaidToggleFeatured.as_view(),
                name='maid_toggle_featured'
            )
        ])
    )
]
