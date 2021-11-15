from django.urls.conf import include, path

from .views import (GeneralEnquiryListCreateAPIView, MaidListAPIView,
                    MaidRetrieveAPIView, PotentialEmployerListCreateAPIView,
                    PotentialEmployerLoginAPIView, SimilarMaidListAPIView)

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
                'sign-up',
                PotentialEmployerListCreateAPIView.as_view()
            ),
            path(
                'login',
                PotentialEmployerLoginAPIView.as_view()
            )
        ])
    )
]
