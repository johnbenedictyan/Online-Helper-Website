# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views
from .views import CustomerPortal

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
    ),
    path(
        'customer-portal/',
        CustomerPortal.as_view(),
        name='stripe_customer_portal'
    )
]
