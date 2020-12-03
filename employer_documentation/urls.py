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
from .views import (
    EmployerBaseUpdateView,
    EmployerDocBaseUpdateView,
)

## Delete Views
from .views import (
    EmployerBaseDeleteView,
)

# Start of Urls

urlpatterns = [
    path(
        '',
        include([
            path(
                'create/',
                EmployerBaseCreateView.as_view(),
                name='employer_base_create'
            ),
            path(
                '<int:employer_base_pk>/',
                include([
                    path(
                        'update/',
                        EmployerBaseUpdateView.as_view(),
                        name='employer_base_update'
                    ),
                    path(
                        'delete/',
                        EmployerBaseDeleteView.as_view(),
                        name='employer_base_delete'
                    ),
                    path(
                        'doc-base/create/',
                        EmployerDocBaseCreateView.as_view(),
                        name='employer_doc_base_create'
                    ),
                    path(
                        'doc-base/<int:employer_doc_base_pk>/update/',
                        EmployerDocBaseUpdateView.as_view(),
                        name='employer_doc_base_update'
                    ),
                ])
            ),
        ]),
    ),
]
