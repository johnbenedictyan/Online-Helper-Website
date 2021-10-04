from django.urls import include, path

from .views import (FeaturedMaidListView, MaidDelete, MaidDetail, MaidList,
                    MaidLoanTransactionUpdate, MaidProfileView,
                    MaidToggleFeatured, MaidTogglePublished,
                    PdfMaidBiodataView)



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
