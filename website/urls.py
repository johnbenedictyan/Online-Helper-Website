# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## Template Views 
from .views import (
    HomeView, AboutUsView, ContactUsView, TermsOfSerivceView, RobotsTxt,
    HowItWorksView
)

## List Views

## Detail Views

## Create Views

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
        path(
            '',
            HomeView.as_view(),
            name='home'
        ),
        path(
            'about-us/',
            AboutUsView.as_view(),
            name='about_us'
        ),
        path(
            'contact-us/',
            ContactUsView.as_view(),
            name='contact_us'
        ),
        path(
            'terms-of-service/',
            TermsOfSerivceView.as_view(),
            name='terms_of_service'
        ),
        path(
            'how-it-works/',
            HowItWorksView.as_view(),
            name='how_it_works'
        ),
        path(
            'robots.txt',
            RobotsTxt.as_view(),
            name="robots_txt"
        )
]
