# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views
from .views import AddToCart, CustomerPortal, RemoveFromCart, ToggleSubscriptionProductArchive, ViewCart

## List Views
from .views import (
    InvoiceList, SubscriptionProductList, SubscriptionProductImageList,
    SubscriptionProductPriceList
)

## Detail Views
from .views import InvoiceDetail

## Create Views
from .views import (
    SubscriptionProductCreate, SubscriptionProductImageCreate,
    SubscriptionProductPriceCreate
)

## Update Views

## Delete Views
from .views import SubscriptionProductImageDelete

## Generic Views
from .views import StripeWebhookView, CheckoutSession

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
                            ),
                            path(
                                'toggle-archive/',
                                ToggleSubscriptionProductArchive.as_view(),
                                name='toggle_subscription_product_archive'
                            )
                        ])
                    )
                ])
            )
        ])
    ),
    path(
        'delete/',
        include([
            path(
                'product/',
                include([
                    path(
                        'image/<slug:pk>/',
                        SubscriptionProductImageDelete.as_view(),
                        name='subscription_product_image_delete'
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
            ),
            path(
                'products/',
                include([
                    path(
                        '',
                        SubscriptionProductList.as_view(),
                        name='subscription_product_list'
                    ),
                    path(
                        '<slug:pk>/',
                        include([
                            path(
                                'images/',
                                SubscriptionProductImageList.as_view(),
                                name='subscription_product_image_list'
                            ),
                            path(
                                'prices/',
                                SubscriptionProductPriceList.as_view(),
                                name='subscription_product_price_list'
                            )
                        ])
                    )
                ])
            ),
        ])
    ),
    path(
        'customer-portal/',
        CustomerPortal.as_view(),
        name='stripe_customer_portal'
    ),
    path(
        'stripe-webhook/',
        StripeWebhookView.as_view(),
        name='stripe_webhook'
    ),
    path(
        'create-checkout-session/',
        CheckoutSession.as_view(),
        name='checkout_session'
    ),
    path(
        'cart/',
        include([
            path(
                'add/<slug:pk>/',
                AddToCart.as_view(),
                name='add_to_cart'
            ),
            path(
                'remove/<slug:pk>/',
                RemoveFromCart.as_view(),
                name='remove_from_cart'
            ),
            path(
                'view/',
                ViewCart.as_view(),
                name='view_cart'
            )
        ])
    )
]
