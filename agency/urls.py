from django.urls import include, path

from .views import (AgencyCreate, AgencyDetail, AgencyList, AgencyOwnerCreate,
                    AgencySignUp)

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                AgencyCreate.as_view(),
                name='agency_create'
            ),
            path(
                '<int:pk>/owner/',
                AgencyOwnerCreate.as_view(),
                name='agency_owner_create'
            )
        ])
    ),
    path(
        'view/',
        include([
            path(
                '',
                AgencyList.as_view(),
                name='agency_list'
            ),
            path(
                '<slug:pk>/',
                AgencyDetail.as_view(),
                name='agency_detail'
            )
        ])
    ),
    path(
        'sign-up/',
        AgencySignUp.as_view(),
        name='agency_sign_up'
    )
]
