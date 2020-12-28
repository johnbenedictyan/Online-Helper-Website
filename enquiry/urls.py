# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views
from .views import DeactivateEnquiryView

## Template Views 
from .views import EnquiryView

## List Views
from .views import EnquiryListView

## Detail Views

## Create Views

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
        path(
            '',
            EnquiryView.as_view(),
            name='enquiry'
        ),
        path(
            'all/',
            EnquiryListView.as_view(),
            name='enquiry'
        ),
        path(
            'deactive/<int:pk>/',
            DeactivateEnquiryView.as_view(),
            name='enquiry'
        )
]
