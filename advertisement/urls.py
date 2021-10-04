from django.urls import include, path

from .views import (AdvertisementCreate, AdvertisementDelete,
                    AdvertisementDetail, AdvertisementList,
                    AdvertisementUpdate)

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                AdvertisementCreate.as_view(),
                name='advertisement_create'
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                '',
                AdvertisementDelete.as_view(),
                name='advertisement_delete'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                '',
                AdvertisementUpdate.as_view(),
                name='advertisement_update'
            )
        ])
    ),
    path(
        'view/',
        include([
            path(
                '',
                AdvertisementList.as_view(),
                name='advertisement_list'
            ),
            path(
                '<int:pk>/',
                AdvertisementDetail.as_view(),
                name='advertisement_detail'
            )
        ])
    )
]
