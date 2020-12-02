# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## List Views
# from .views import 

## Detail Views
# from .views import 

## Create Views
from .views import EmployerBaseCreate

## Update Views
from .views import EmployerBaseUpdate

## Delete Views
from .views import EmployerBaseDelete

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                'employer/',
                EmployerBaseCreate.as_view(),
                name='employer_base_create'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                'employer/<int:pk>/',
                EmployerBaseUpdate.as_view(),
                name='employer_base_update'
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                'employer/<int:pk>/',
                EmployerBaseDelete.as_view(),
                name='employer_base_delete'
            )
        ])
    ),
    # path(
    #     'view/',
    #     include([
    #         path(
    #             'employer',
    #             EmployerBaseList.as_view(),
    #             name='employer_base_list'
    #         ),
    #         path(
    #             'employer/<int:pk>/',
    #             EmployerBaseDetail.as_view(),
    #             name='employer_base_detail'
    #         )
    #     ])
    # )
]
