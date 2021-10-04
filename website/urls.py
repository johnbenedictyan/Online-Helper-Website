
from django.urls import include, path


from .views import (AboutUsView, AdminPanelEnquiryListView, AdminPanelView,
                    ContactUsView, Error403View, Error404View, Error500View,
                    FAQView, HomeView, HowItWorksView, LoaderIOView,
                    PrivacyPolicyView, RobotsTxt, SitemapView,
                    TermsAndConditionsAgencyView, TermsAndConditionsUserView,
                    UsefulLinksView)



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
        'terms-and-conditions/',
        include([
            path(
                'agencies/',
                TermsAndConditionsAgencyView.as_view(),
                name='terms_and_conditions_agency'
            ),
            path(
                'users/',
                TermsAndConditionsUserView.as_view(),
                name='terms_and_conditions_user'
            )
        ])
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
        'useful-links/',
        UsefulLinksView.as_view(),
        name='useful_links'
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
                '403/',
                Error403View.as_view(),
                name='error_403'
            ),
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
    ),
    path(
        'sitemap.xml',
        SitemapView.as_view(),
        name="site_map"
    ),
    path(
        'loaderio-03efabeaabfb72e90f648bd86d913ad9/',
        LoaderIOView.as_view(),
        name='loader_io_view'
    )
]
