# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views
from .views import DeactivateGeneralEnquiryView, ToggleApproveEnquiryView

## Template Views 

## List Views
from .views import EnquiryListView

## Detail Views

## Create Views
from .views import GeneralEnquiryView, AgencyEnquiryView, MaidEnquiryView

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
    path(
        'general/',
        GeneralEnquiryView.as_view(),
        name='general_enquiry'
    ),
    path(
        'agency/<int:pk/',
        AgencyEnquiryView.as_view(),
        name='agency_enquiry'
    ),
    path(
        'maid/<int:pk/',
        MaidEnquiryView.as_view(),
        name='maid_enquiry'
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
    )
]
