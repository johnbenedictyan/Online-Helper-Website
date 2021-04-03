# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## Template Views 
from .views import (
    HomeView, AboutUsView, ContactUsView, TermsOfSerivceView, RobotsTxt,
    HowItWorksView, FAQView, AdminPanelView, PrivacyPolicyView,
    AdminPanelEnquiryListView, Error404View, Error500View
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
        'privacy-policy/',
        PrivacyPolicyView.as_view(),
        name='privacy_policy'
    ),
    path(
        'how-it-works/',
        HowItWorksView.as_view(),
        name='how_it_works'
    ),
    path(
        'faq/',
        FAQView.as_view(),
        name='faq'
    ),
    path(
        'admin-panel/',
        include([
            path(
                '',
                AdminPanelView.as_view(),
                name='admin_panel'
            ),
            path(
                'enquiries/',
                AdminPanelEnquiryListView,
                name='admin_panel_enquiry_list'
            )
        ])
    ),
    path(
        'error/',
        include([
            path(
                '404/',
                Error404View.as_view(),
                name='error_404'
            ),
            path(
                '500/',
                Error500View.as_view(),
                name='error_500'
            )
        ])
    ),
    path(
        'robots.txt',
        RobotsTxt.as_view(),
        name="robots_txt"
    )
]
