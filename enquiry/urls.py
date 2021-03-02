# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views
from .views import DeactivateEnquiryView

## Template Views 

## List Views
from .views import EnquiryListView

## Detail Views

## Create Views
from .views import GeneralEnquiryView

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
        path(
            '',
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
            DeactivateEnquiryView.as_view(),
            name='deactivate_enquiry'
        )
]
