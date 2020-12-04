# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## List Views
from .views import (
    EmployerBaseListView,
    EmployerDocBaseListView,
)

## Detail Views
from .views import (
    EmployerBaseDetailView,
    EmployerDocBaseDetailView,
)

## Create Views
from .views import (
    EmployerBaseCreateView,
    EmployerExtraInfoCreateView,
    EmployerDocBaseCreateView,
)

## Update Views
from .views import (
    EmployerBaseUpdateView,
    EmployerExtraInfoUpdateView,
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
                'employers-list/',
                EmployerBaseListView.as_view(),
                name='employer_base_list'
            ),
            path(
                '<int:employer_base_pk>/',
                include([
                    path(
                        'detail/',
                        EmployerBaseDetailView.as_view(),
                        name='employer_base_detail'
                    ),
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
                        'extra-info/create/',
                        EmployerExtraInfoCreateView.as_view(),
                        name='employer_extra_info_create'
                    ),
                    path(
                        'extra-info/<int:employer_extra_info_pk>/update/',
                        EmployerExtraInfoUpdateView.as_view(),
                        name='employer_extra_info_update'
                    ),
                    path(
                        'doc-base/create/',
                        EmployerDocBaseCreateView.as_view(),
                        name='employer_doc_base_create'
                    ),
                    path(
                        'doc-base/list/',
                        EmployerDocBaseListView.as_view(),
                        name='employer_doc_base_list'
                    ),
                    path(
                        'doc-base/<int:employer_doc_base_pk>/detail/',
                        EmployerDocBaseDetailView.as_view(),
                        name='employer_doc_base_detail'
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
