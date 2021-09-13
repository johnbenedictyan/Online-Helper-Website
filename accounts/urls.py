# Django Imports
from django.urls import include, path
from django.contrib.auth import views as auth_views

# App Imports
from .views import (
    SignInView, AgencySignInView, SignOutView, PotentialEmployerDetail,
    PotentialEmployerCreate, PotentialEmployerUpdate, PotentialEmployerDelete,
    CustomPasswordResetView, UserEmailUpdate
)

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                '',
                PotentialEmployerCreate.as_view(),
                name='potential_employer_create'
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                '',
                PotentialEmployerDelete.as_view(),
                name='potential_employer_delete'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                '',
                PotentialEmployerUpdate.as_view(),
                name='potential_employer_update'
            ),
            path(
                'email',
                UserEmailUpdate.as_view(),
                name='user_email_update'
            )
        ])
    ),
    path(
        'profile/',
        PotentialEmployerDetail.as_view(),
        name='potential_employer_detail'
    ),
    path(
        'login/',
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
    path(
        'oauth/',
        include(
            'social_django.urls',
            namespace="social"
        )
    ),
    path(
        'password-reset/',
        CustomPasswordResetView.as_view(),
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
