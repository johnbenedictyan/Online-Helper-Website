# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## List Views
from .views import AdvertisementList

## Detail Views
from .views import AdvertisementDetail

## Create Views
from .views import AdvertisementCreate

## Update Views
from .views import AdvertisementUpdate

## Delete Views
from .views import AdvertisementDelete

# Start of Urls

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
