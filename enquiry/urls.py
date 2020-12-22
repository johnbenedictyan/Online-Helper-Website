# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## Template Views 
from .views import GeneralEnquiryView, SpecificEnquiryView

## List Views

## Detail Views

## Create Views

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
            'specific/',
            SpecificEnquiryView.as_view(),
            name='specific_enquiry'
        )
]
