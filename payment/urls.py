# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## List Views
from .views import InvoiceList

## Detail Views
from .views import InvoiceDetail

## Create Views

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
    path(
        'view/',
        include([
            path(
                '',
                InvoiceList.as_view(),
                name='invoice_list'
            ),
            path(
                '<int:pk>/',
                InvoiceDetail.as_view(),
                name='invoice_detail'
            )
        ])
    )
]
