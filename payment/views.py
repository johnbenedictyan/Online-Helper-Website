from datetime import datetime
from typing import Any, Dict, Optional

import stripe
from agency.mixins import AgencyOwnerRequiredMixin, GetAuthorityMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet as QS
from django.http.request import HttpRequest as req
from django.http.response import HttpResponse as res
from django.http.response import HttpResponseBase as RESBASE
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from onlinemaid.types import T

from .constants import (SubscriptionLimitMap, SubscriptionStatusChoices,
                        SubscriptionTypeChoices)
from .models import Customer, Invoice, Subscription

# Stripe Settings
stripe.api_key = settings.STRIPE_SECRET_KEY


class ViewCart(TemplateView):
    template_name = 'base/cart.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        current_cart = self.request.session.get('cart', [])
        self.request.session['cart'] = current_cart

        context['cart'] = Subscription.objects.filter(
            pk__in=current_cart
        )
        return context


class CustomerPortal(AgencyOwnerRequiredMixin, GetAuthorityMixin,
                     RedirectView):
    authority = ''
    agency_id = ''

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer_id = Customer.objects.get(
            agency__pk=self.agency_id
        ).pk
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=self.request.build_absolute_uri(
                reverse_lazy('dashboard_home')
            ),
        )
        return session.url


class CheckoutSuccess(RedirectView):
    http_method_names = ['get']
    pattern_name = 'dashboard_home'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        self.request.session['cart'] = []
        messages.success(
            self.request,
            'Payment Success',
            extra_tags='success'
        )
        return super().get_redirect_url()


class CheckoutCancel(RedirectView):
    http_method_names = ['get']
    pattern_name = 'view_cart'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        messages.info(
            self.request,
            'Payment Cancelled',
            extra_tags='info'
        )
        return super().get_redirect_url()


class AddToCart(View):
    pattern_name = 'view_cart'

    def post(self, request: req, *args: Any, **kwargs: Any) -> RESBASE:
        if (
            request.POST.get('agencySubscriptionPlan')
            or request.POST.get('advertisementPlan')
        ):
            current_cart = self.request.session.get('cart', [])
            agency = self.request.user.agency_owner.agency
            if request.POST.get('agencySubscriptionPlan'):
                pk = request.POST.get('agencySubscriptionPlan')
            else:
                pk = request.POST.get('advertisementPlan')
            try:
                current_subscription = Subscription.objects.get(
                    customer=Customer.objects.get(
                        agency=agency
                    ),
                    stripe_id=pk
                )
            except Subscription.DoesNotExist:
                # messages.error(
                #     self.request,
                #     'This product does not exist'
                # )
                # return redirect('dashboard_agency_plan_list')
                new_subscription = Subscription.objects.create(
                    customer=Customer.objects.get(
                        agency=agency
                    ),
                    price=1,
                    stripe_id=pk
                )
                current_cart.append(
                    new_subscription.stripe_id
                )
                self.request.session['cart'] = current_cart
            else:
                if SubscriptionLimitMap[pk]['type'] == 'plan':
                    if Subscription.objects.filter(
                        customer=Customer.objects.get(
                            agency=agency
                        ),
                        subscription_type=SubscriptionTypeChoices.PLAN,
                        status=SubscriptionStatusChoices.ACTIVE,
                        end_date__gt=timezone.now()
                    ).count() >= 1:
                        messages.warning(
                            self.request,
                            f'''
                            You already have an active subscription.
                            If you would like to change that subscription,
                            <a href="{reverse_lazy('stripe_customer_portal')}">
                                Click Here
                            </a>
                            ''',
                            extra_tags='error'
                        )
                        return reverse_lazy('dashboard_agency_plan_list')

        else:
            return redirect('dashboard_agency_plan_list')


class RemoveFromCart(RedirectView):
    pattern_name = 'view_cart'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        current_cart = self.request.session.get('cart', [])
        try:
            select_product_price = Subscription.objects.get(
                pk=kwargs.get('pk')
            )
        except Subscription.DoesNotExist:
            messages.error(
                self.request,
                'This product does not exist'
            )
        else:
            if select_product_price.pk not in current_cart:
                messages.error(
                    self.request,
                    'This product is not in your cart'
                )
            else:
                current_cart.remove(
                    select_product_price.pk
                )
                self.request.session['cart'] = current_cart
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)


class InvoiceList(LoginRequiredMixin, ListView):
    context_object_name = 'invoice'
    http_method_names = ['get']
    model = Invoice
    template_name = 'invoice-list.html'

    def get_queryset(self) -> QS[T]:
        return Invoice.objects.filter(
            agency__pk=self.request.user.pk
        )


class InvoiceDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'invoice'
    http_method_names = ['get']
    model = Invoice
    template_name = 'invoice-detail.html'


class CheckoutSession(View):
    http_method_names = ['post']

    def post(self, request: req, *args: Any, **kwargs: Any) -> RESBASE:
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(
                name='Agency Owners'
            ).exists():
                try:
                    checkout_session = stripe.checkout.Session.create(
                        success_url=request.build_absolute_uri(
                            reverse_lazy('checkout_success')
                        ),
                        cancel_url=request.build_absolute_uri(
                            reverse_lazy('checkout_cancel')
                        ),
                        customer=Customer.objects.get(
                            agency__pk=request.user.agency_owner.agency.pk
                        ).pk,
                        payment_method_types=['card'],
                        mode='subscription',
                        line_items=[
                            {
                                'price': i,
                                'quantity': 1
                            } for i in request.session.get('cart')
                        ]
                    )
                    return JsonResponse(
                        {
                            'sessionId': checkout_session['id']
                        }
                    )
                except Exception as e:
                    return JsonResponse(
                        {
                            'error': {
                                'message': str(e)
                            }
                        },
                        status=400
                    )
            else:
                return JsonResponse(
                    {
                        'error': {
                            'message': 'Agency Owner Required'
                        }
                    },
                    status=400
                )
        else:
            return JsonResponse(
                {
                    'error': {
                        'message': 'Login Required'
                    }
                },
                status=400
            )


class StripeWebhookView(View):
    http_method_names = ['post']
    endpoint_secret = 'whsec_7VRZrfVz3dwOCo49n2uLdIyibwXpOdeo'

    @method_decorator(csrf_exempt)
    def dispatch(self, request: req, *args: Any, **kwargs: Any) -> RESBASE:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: req, *args: Any, **kwargs: Any) -> RESBASE:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.endpoint_secret
            )
        except ValueError:
            # Invalid payload
            return res(status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return res(status=400)
        else:
            if event.type == 'invoice.created':
                Subscription.objects.get_or_create(
                    id=event.data.object.subscription,
                    customer=Customer.objects.get(
                        pk=event.data.object.customer
                    ),
                    product=SubscriptionProduct.objects.get(
                        pk=event.data.object.lines.data[0].price.product
                    ),
                    status=SubscriptionStatusChoices.UNPAID
                )
            if event.type == 'invoice.paid':
                subscription = Subscription.objects.get(
                    id=event.data.object.subscription
                )
                subscription.start_date = datetime.utcfromtimestamp(
                    event.data.object.lines.data[0].period.start
                )
                subscription.end_date = datetime.utcfromtimestamp(
                    event.data.object.lines.data[0].period.end
                )
                subscription.status = SubscriptionStatusChoices.ACTIVE
                subscription.save()

            if event.type == 'invoice.payment_failed':
                print(event)

            return HttpResponse(status=200)
