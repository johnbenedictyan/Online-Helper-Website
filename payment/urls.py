from django.urls import include, path

from .views import (AddToCart, CheckoutCancel, CheckoutSession,
                    CheckoutSuccess, CustomerPortal, InvoiceDetail,
                    InvoiceList, RemoveFromCart, StripeWebhookView, ViewCart)


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
        'checkout/',
        include([
            path(
                'success/',
                CheckoutSuccess.as_view(),
                name='checkout_success'
            ),
            path(
                'cancel/',
                CheckoutCancel.as_view(),
                name='checkout_cancel'
            )
        ])
    ),
    path(
        'cart/',
        include([
            path(
                'add/',
                AddToCart.as_view(),
                name='add_to_cart'
            ),
            path(
                'remove/<slug:sub_type>/<int:pk>/',
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
