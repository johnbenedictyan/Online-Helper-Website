from django.urls.conf import include, path

from .views import GeneralEnquiryCreateAPIView, MaidListAPIView, MaidRetrieveAPIView, SimilarMaidListAPIView

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
                GeneralEnquiryCreateAPIView.as_view()
            ),
        ])
    )
]
