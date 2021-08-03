# Django Imports
from django.urls import path
from django.urls.conf import include

# App Imports
from .views import (
    DeactivateGeneralEnquiryView, ToggleApproveEnquiryView,
    SuccessfulEnquiryView, EnquiryListView, GeneralEnquiryView,
    ApproveGeneralEnquiryView, ApproveShortlistedlEnquiryView,
    RejectGeneralEnquiryView, RejectShortlistedEnquiryView
)

# Start of Urls

urlpatterns = [
    path(
        'general/',
        GeneralEnquiryView.as_view(),
        name='general_enquiry'
    ),
    path(
        'all/',
        EnquiryListView.as_view(),
        name='enquiry_list'
    ),
    path(
        'deactive/<int:pk>/',
        DeactivateGeneralEnquiryView.as_view(),
        name='deactivate_enquiry'
    ),
    path(
        'toggle-approve/<int:pk>/',
        ToggleApproveEnquiryView.as_view(),
        name='toggle_approve_enquiry'
    ),
    path(
        'approve',
        include([
            path(
                'general/<int:pk>/',
                ApproveGeneralEnquiryView.as_view(),
                name='approve_general_enquiry'
            ),
            path(
                'shortlisted/<int:pk>/',
                ApproveShortlistedlEnquiryView.as_view(),
                name='approve_shortlisted_enquiry'
            )
        ])
    ),
    path(
        'reject',
        include([
            path(
                'general/<int:pk>/',
                RejectGeneralEnquiryView.as_view(),
                name='reject_general_enquiry'
            ),
            path(
                'shortlisted/<int:pk>/',
                RejectShortlistedEnquiryView.as_view(),
                name='reject_shortlisted_enquiry'
            )
        ])
    ),
    path(
        'success/',
        SuccessfulEnquiryView.as_view(),
        name='successful_enquiry'
    )
]
