from datetime import datetime
from typing import Any, Dict, Optional

import stripe
from agency.mixins import (AgencyOwnerRequiredMixin, GetAuthorityMixin,
                           OMStaffRequiredMixin)
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet as QS
from django.http.request import HttpRequest as REQ
from django.http.response import HttpResponse as RES
from django.http.response import HttpResponseBase as RESBASE
from django.http.response import JsonResponse
from django.shortcuts import get_list_or_404, redirect
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from onlinemaid.mixins import SuccessMessageMixin
from onlinemaid.types import T


from .constants import (SubscriptionLimitMap, SubscriptionStatusChoices,
                        SubscriptionTypeChoices)
from .forms import (SubscriptionProductCreationForm,
                    SubscriptionProductImageCreationForm,
                    SubscriptionProductPriceCreationForm)
from .models import (Customer, Invoice, Subscription, SubscriptionProduct,
                     SubscriptionProductImage, SubscriptionProductPrice)

# Stripe Settings
stripe.api_key = settings.STRIPE_SECRET_KEY




class ViewCart(TemplateView):
    template_name = 'base/cart.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        current_cart = self.request.session.get('cart', [])
        self.request.session['cart'] = current_cart

        context['cart'] = SubscriptionProductPrice.objects.filter(
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


class ToggleSubscriptionProductArchive(RedirectView):
    http_method_names = ['get']
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        try:
            subscription_prod = SubscriptionProduct.objects.get(
                pk=self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        except SubscriptionProduct.DoesNotExist:
            messages.error(
                self.request,
                'This subscription product does not exist'
            )
        else:
            try:
                stripe.Product.modify(
                    subscription_prod.pk,
                    active=not SubscriptionProduct.archived
                )
            except Exception as e:
                print(e)
            else:
                subscription_prod.archived = not subscription_prod.archived
                subscription_prod.save()
            kwargs.pop(self.pk_url_kwarg)
        finally:
            return reverse_lazy(
                'admin_panel'
            )


class AddToCart(View):
    pattern_name = 'view_cart'

    def post(self, request: REQ, *args: Any, **kwargs: Any) -> RESBASE:
        if (
            request.POST.get('agencySubscriptionPlan')
            or request.POST.get('advertisementPlan')
        ):
            current_cart = self.request.session.get('cart', [])
            if request.POST.get('agencySubscriptionPlan'):
                pk = request.POST.get('agencySubscriptionPlan')
            else:
                pk = request.POST.get('advertisementPlan')
            try:
                selected_product_price = SubscriptionProductPrice.objects.get(
                    pk=pk
                )
            except SubscriptionProductPrice.DoesNotExist:
                messages.error(
                    self.request,
                    'This product does not exist'
                )
                return redirect('dashboard_agency_plan_list')
            else:
                product = selected_product_price.subscription_product
                agency = self.request.user.agency_owner.agency
                if SubscriptionLimitMap[product.pk]['type'] == 'plan':
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

                current_cart.append(
                    selected_product_price.pk
                )
                self.request.session['cart'] = current_cart
        else:
            return redirect('dashboard_agency_plan_list')


class RemoveFromCart(RedirectView):
    pattern_name = 'view_cart'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        current_cart = self.request.session.get('cart', [])
        try:
            select_product_price = SubscriptionProductPrice.objects.get(
                pk=kwargs.get('pk')
            )
        except SubscriptionProductPrice.DoesNotExist:
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


class SubscriptionProductList(OMStaffRequiredMixin, ListView):
    context_object_name = 'subscription_products'
    http_method_names = ['get']
    model = SubscriptionProduct
    template_name = 'list/subscription-product-list.html'


class SubscriptionProductImageList(OMStaffRequiredMixin, ListView):
    context_object_name = 'subscription_product_images'
    http_method_names = ['get']
    model = SubscriptionProductImage
    template_name = 'list/subscription-product-image-list.html'

    def get_queryset(self) -> QS[T]:
        return get_list_or_404(
            SubscriptionProductImage,
            subscription_product__pk=self.kwargs.get('pk')
        )


class SubscriptionProductPriceList(OMStaffRequiredMixin, ListView):
    context_object_name = 'subscription_product_prices'
    http_method_names = ['get']
    model = SubscriptionProductPrice
    template_name = 'list/subscription-product-price-list.html'

    def get_queryset(self) -> QS[T]:
        return get_list_or_404(
            SubscriptionProductPrice,
            subscription_product__pk=self.kwargs.get('pk')
        )


class InvoiceDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'invoice'
    http_method_names = ['get']
    model = Invoice
    template_name = 'invoice-detail.html'


class SubscriptionProductCreate(OMStaffRequiredMixin,
                                SuccessMessageMixin, CreateView):
    context_object_name = 'subscription_product'
    form_class = SubscriptionProductCreationForm
    http_method_names = ['get', 'post']
    model = SubscriptionProduct
    template_name = 'create/subscription-product-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Subscription Product created'

    def form_valid(self, form) -> RES:
        cleaned_data = form.cleaned_data
        subscription_product_name = cleaned_data.get('name')
        subscription_product_description = cleaned_data.get('description')
        subscription_product_active = cleaned_data.get('active')
        try:
            stripe_product = stripe.Product.create(
                name=subscription_product_name,
                description=subscription_product_description,
                active=subscription_product_active
            )
        except Exception:
            form.add_error(None, 'Something wrong happened. Please try again!')
        else:
            form.instance.id = stripe_product.id
        return super().form_valid(form)


class SubscriptionProductImageCreate(OMStaffRequiredMixin,
                                     SuccessMessageMixin, CreateView):
    context_object_name = 'subscription_product_image'
    form_class = SubscriptionProductImageCreationForm
    http_method_names = ['get', 'post']
    model = SubscriptionProductImage
    template_name = 'create/subscription-product-image-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Subscription Product Image created'

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'subscription_product_id': self.kwargs.get(
                self.pk_url_kwarg
            )
        })
        return kwargs


class SubscriptionProductPriceCreate(OMStaffRequiredMixin,
                                     SuccessMessageMixin, CreateView):
    context_object_name = 'subscription_product_price'
    form_class = SubscriptionProductPriceCreationForm
    http_method_names = ['get', 'post']
    model = SubscriptionProductPrice
    template_name = 'create/subscription-product-price-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Subscription Product Price created'

    def form_valid(self, form) -> RES:
        cleaned_data = form.cleaned_data
        subscription_product = SubscriptionProduct.objects.get(
            pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        try:
            stripe_product = stripe.Product.retrieve(
                subscription_product.pk
            )
        except Exception:
            form.add_error(None, 'This product does not exist!')
        else:
            subscription_product_currency = cleaned_data.get('currency')
            subscription_product_interval = cleaned_data.get('interval')
            subscription_product_interval_count = cleaned_data.get(
                'interval_count'
            )
            subscription_product_unit_amount = cleaned_data.get(
                'unit_amount'
            )
            subscription_product_active = cleaned_data.get('active')
            try:
                stripe_price = stripe.Price.create(
                    unit_amount=subscription_product_unit_amount,
                    currency=subscription_product_currency,
                    recurring={
                        'aggregate_usage': None,
                        'interval': subscription_product_interval,
                        'interval_count': subscription_product_interval_count,
                        'usage_type': 'licensed'
                    },
                    active=subscription_product_active,
                    product=stripe_product.id
                )
            except Exception:
                form.add_error(
                    None,
                    _('Something wrong happened. Please try again!')
                )
            else:
                form.instance.id = stripe_price.id
                form.instance.subscription_product = subscription_product
        return super().form_valid(form)


class SubscriptionProductImageDelete(OMStaffRequiredMixin,
                                     SuccessMessageMixin, DeleteView):
    context_object_name = 'subscription_product_image'
    http_method_names = ['post']
    model = SubscriptionProductImage
    success_url = reverse_lazy('admin_panel')
    success_message = 'Subscription Product Image deleted'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        product_images = [
            img.photo.url for img in SubscriptionProductImage.objects.filter(
                subscription_product=self.object
            )
        ]
        try:
            stripe.Product.modify(
                self.object.pk,
                images=product_images
            )
        except Exception as e:
            print(e)

        return super().delete(request, *args, **kwargs)


class CheckoutSession(View):
    http_method_names = ['post']

    def post(self, request: REQ, *args: Any, **kwargs: Any) -> RESBASE:
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
    def dispatch(self, request: REQ, *args: Any, **kwargs: Any) -> RESBASE:
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: REQ, *args: Any, **kwargs: Any) -> RESBASE:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.endpoint_secret
            )
        except ValueError:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return HttpResponse(status=400)
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
