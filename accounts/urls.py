# Imports from django
from django.urls import include, path
from django.contrib.auth import views as auth_views

# Imports from foreign installed apps

# Imports from local app
from .forms import SignInForm

## Create Views
from .views import EmployerCreate

## Update Views
from .views import EmployerUpdate

## Delete Views
from .views import EmployerDelete

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                EmployerCreate.as_view(),
                name='employer_create'
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                '',
                EmployerDelete.as_view(),
                name='employer_delete'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                '',
                EmployerUpdate.as_view(),
                name='employer_update'
            )
        ])
    ),
    path(
        'sign-in/',
        auth_views.LoginView.as_view(
            template_name='sign-in.html',
            authentication_form=SignInForm
        ),
        name='sign_in'
    ),
]
