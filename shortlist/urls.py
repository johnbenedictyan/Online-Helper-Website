# Django Imports
from django.urls import path

# App Imports
from .views import AddTo, RemoveFrom, ViewShortlist

# Start of Urls

urlpatterns = [
    path(
        'add/<int:pk>/',
        AddTo.as_view(),
        name='add_to_shortlist'
    ),
    path(
        'remove/<int:pk>/',
        RemoveFrom.as_view(),
        name='remove_from_shortlist'
    ),
    path(
        'view/',
        ViewShortlist.as_view(),
        name='view_shortlist'
    ),
]
