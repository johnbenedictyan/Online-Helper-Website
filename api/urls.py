from django.urls.conf import include, path

from .views import (GeneralEnquiryListCreateAPIView, MaidListAPIView,
                    MaidRetrieveAPIView, PotentialEmployerCreateAPIView,
                    SimilarMaidListAPIView)

urlpatterns = [
    path(
        'maids/',
        include([
            path(
                '',
                MaidListAPIView.as_view()
            ),
            path(
                '<int:pk>/',
                include([
                    path(
                        '',
                        MaidRetrieveAPIView.as_view()
                    ),
                    path(
                        'similar/',
                        SimilarMaidListAPIView.as_view()
                    )
                ])

            )
        ])
    ),
    path(
        'enquiries/',
        include([
            path(
                '',
                GeneralEnquiryListCreateAPIView.as_view()
            ),
        ])
    ),
    path(
        'users/',
        include([
            path(
                'pe',
                PotentialEmployerCreateAPIView.as_view()
            ),
        ])
    )
]
