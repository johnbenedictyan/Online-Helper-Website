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
from .views import (
    SubscriptionProductCreate, SubscriptionProductImageCreate,
    SubscriptionProductPriceCreate
)

## Update Views

## Delete Views

# Start of Urls

urlpatterns = [
    path(
        'create/',
        include([
            path(
                'product/',
                include([
                    path(
                        '',
                        SubscriptionProductCreate.as_view(),
                        name='subscription_product_create'
                    ),
                    path(
                        '<slug:pk>/',
                        include([
                            path(
                                'image/',
                                SubscriptionProductImageCreate.as_view(),
                                name='subscription_product_image_create'
                            ),
                            path(
                                'price/',
                                SubscriptionProductPriceCreate.as_view(),
                                name='subscription_product_price_create'
                            )
                        ])
                    )
                ])
            )
        ])
    ),
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
