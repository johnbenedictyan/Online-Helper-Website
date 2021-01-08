# Imports from django
from django.urls import include, path
from django.contrib.auth import views as auth_views

# Imports from foreign installed apps

# Imports from local app
from .forms import SignInForm

## Views that extend inbuilt django views
from .views import SignInView, AgencySignInView

## Redirect Views 
from .views import SignOutView

## Detail Views
from .views import EmployerDetail

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
        'profile/',
        EmployerDetail.as_view(),
        name='employer_detail'
    ),
    path(
        'sign-in/',
        include([
            path(
                'employers',
                SignInView.as_view(),
                name='sign_in'
            ),
            path(
                'agency',
                AgencySignInView.as_view(),
                name='agency_sign_in'
            )
        ])
    ),
    path(
        'sign-out/',
        SignOutView.as_view(),
        name='sign_out'
    ),
    path('oauth/',include('social_django.urls', namespace="social")),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_complete'
    )
]
