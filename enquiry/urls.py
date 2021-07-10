# Django Imports
from django.urls import path

# App Imports
from .views import (
    DeactivateGeneralEnquiryView, ToggleApproveEnquiryView,
    SuccessfulEnquiryView, EnquiryListView, GeneralEnquiryView
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
        'success/',
        SuccessfulEnquiryView.as_view(),
        name='successful_enquiry'
    )
]
