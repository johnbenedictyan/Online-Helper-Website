# Django Imports
from django.urls import include, path

# Foreign Apps Imports

# Imports from local app

# Form Views

# Redirect Views
from .views import MaidTogglePublished, MaidToggleFeatured

# List Views
from .views import MaidList

# Detail Views
from .views import MaidDetail, PdfMaidBiodataView

# Create Views

# Update Views
from .views import MaidLoanTransactionUpdate

# Delete Views
from .views import MaidDelete

# Generic Views
from .views import MaidProfileView, FeaturedMaidListView

# Start of Urls

urlpatterns = [
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
                'aft/<int:loan_transaction_pk>/',
                MaidLoanTransactionUpdate.as_view(),
                name='maid_loan_transaction_update'
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
                'published/',
                MaidTogglePublished.as_view(),
                name='maid_toggle_published'
            ),
            path(
                'featured/',
                MaidToggleFeatured.as_view(),
                name='maid_toggle_featured'
            )
        ])
    )
]
