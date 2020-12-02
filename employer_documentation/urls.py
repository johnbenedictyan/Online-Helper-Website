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
# from .views import 

## Delete Views
# from .views import 

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                'employer',
                EmployerBaseCreate.as_view(),
                name='employer_base_create'
            )
        ])
    ),
    # path(
    #     'delete/',
    #     include([
    #         path(
    #             'employer',
    #             EmployerBaseDelete.as_view(),
    #             name='employer_base_delete'
    #         )
    #     ])
    # ),
    # path(
    #     'update/',
    #     include([
    #         path(
    #             'employer',
    #             EmployerBaseUpdate.as_view(),
    #             name='employer_base_update'
    #         )
    #     ])
    # ),
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
