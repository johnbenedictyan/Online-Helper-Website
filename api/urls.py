from django.urls.conf import include, path

from .views import MaidListAPIView, MaidRetrieveAPIView


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
                MaidRetrieveAPIView.as_view()
            )
        ])
    )
]
