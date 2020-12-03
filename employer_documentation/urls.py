# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## List Views
# from .views import 

## Detail Views
# from .views import 

## Create Views
from .views import (
    EmployerBaseCreateView,
    EmployerDocBaseCreateView,
)

## Update Views
from .views import EmployerBaseUpdateView

## Delete Views
from .views import EmployerBaseDeleteView

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                'employer/',
                EmployerBaseCreateView.as_view(),
                name='employer_base_create'
            ),
            path(
                'employer-doc-base/<int:pk>/',
                EmployerDocBaseCreateView.as_view(),
                name='employer_doc_base_create'
            ),
        ])
    ),
    path(
        'update/',
        include([
            path(
                'employer/<int:pk>/',
                EmployerBaseUpdateView.as_view(),
                name='employer_base_update'
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                'employer/<int:pk>/',
                EmployerBaseDeleteView.as_view(),
                name='employer_base_delete'
            )
        ])
    ),
]
