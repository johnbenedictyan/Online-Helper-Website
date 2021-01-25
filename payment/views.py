# Imports from modules
import json

# Imports from django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import (
    HttpResponse, HttpResponseRedirect, JsonResponse
)
from django.shortcuts import get_list_or_404
from django.urls.base import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

# Imports from project-wide files

# Imports from foreign installed apps
import stripe
from stripe.api_resources import line_item, payment_method, subscription
from agency.mixins import (
    AgencyOwnerRequiredMixin, GetAuthorityMixin, OnlineMaidStaffRequiredMixin
)
from onlinemaid.mixins import SuccessMessageMixin

# Imports from local app
from .forms import (
    SubscriptionProductCreationForm, SubscriptionProductImageCreationForm,
    SubscriptionProductPriceCreationForm
)
from .models import (
    Invoice, Customer, SubscriptionProduct, SubscriptionProductPrice,
    SubscriptionProductImage
)

# Stripe Settings
stripe.api_key = settings.STRIPE_SECRET_KEY

# Start of Views

# Template Views
class ViewCart(TemplateView):
    template_name = 'base/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_cart = self.request.session.get('cart', [])
        self.request.session['cart'] = current_cart

        context['cart'] = SubscriptionProductPrice.objects.filter(
            pk__in=current_cart
        )
        return context

class CheckoutSuccess(TemplateView):
    template_name = 'base/checkout-success.html'
    
# Redirect Views
class CustomerPortal(AgencyOwnerRequiredMixin, GetAuthorityMixin,
                     RedirectView):
    authority = ''
    agency_id = ''
    
    def get_redirect_url(self, *args, **kwargs):
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

class CheckoutCancel(RedirectView):
    http_method_names = ['get']
    pattern_name = None
    
    def get_redirect_url(self, *args, **kwargs):
        messages.info(
            self.request,
            'Payment Cancelled',
            extra_tags='info'
        )
        return super().get_redirect_url()

class ToggleSubscriptionProductArchive(RedirectView):
    http_method_names = ['get']
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        try:
            subscription_prod = SubscriptionProduct.objects.get(
                pk = self.kwargs.get(
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
                    active = not SubscriptionProduct.archived
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

class AddToCart(RedirectView):
    pattern_name = 'view_cart'

    def get_redirect_url(self, *args, **kwargs):
        current_cart = self.request.session.get('cart', [])
        try:
            select_product_price = SubscriptionProductPrice.objects.get(
                pk = kwargs.get('pk')
            )
        except SubscriptionProductPrice.DoesNotExist:
            messages.error(
                self.request,
                'This product does not exist'
            )
        else:
            current_cart.append(
                select_product_price.pk
            )
            self.request.session['cart'] = current_cart
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

class RemoveFromCart(RedirectView):
    pattern_name = 'view_cart'

    def get_redirect_url(self, *args, **kwargs):
        current_cart = self.request.session.get('cart', [])
        try:
            select_product_price = SubscriptionProductPrice.objects.get(
                pk = kwargs.get('pk')
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

# List Views
class InvoiceList(LoginRequiredMixin, ListView):
    context_object_name = 'invoice'
    http_method_names = ['get']
    model = Invoice
    template_name = 'invoice-list.html'

    def get_queryset(self):
        return Invoice.objects.filter(
            agency__pk = self.request.user.pk
        )

class SubscriptionProductList(OnlineMaidStaffRequiredMixin, ListView):
    context_object_name = 'subscription_products'
    http_method_names = ['get']
    model = SubscriptionProduct
    template_name = 'list/subscription-product-list.html'
    
class SubscriptionProductImageList(OnlineMaidStaffRequiredMixin, ListView):
    context_object_name = 'subscription_product_images'
    http_method_names = ['get']
    model = SubscriptionProductImage
    template_name = 'list/subscription-product-image-list.html'
    
    def get_queryset(self):
        return get_list_or_404(
            SubscriptionProductImage,
            subscription_product__pk = self.kwargs.get('pk')
        )

class SubscriptionProductPriceList(OnlineMaidStaffRequiredMixin, ListView):
    context_object_name = 'subscription_product_prices'
    http_method_names = ['get']
    model = SubscriptionProductPrice
    template_name = 'list/subscription-product-price-list.html'
    
    def get_queryset(self):
        return get_list_or_404(
            SubscriptionProductPrice,
            subscription_product__pk = self.kwargs.get('pk')
        )

# Detail Views
class InvoiceDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'invoice'
    http_method_names = ['get']
    model = Invoice
    template_name = 'invoice-detail.html'

# Create Views
class SubscriptionProductCreate(OnlineMaidStaffRequiredMixin,
                                SuccessMessageMixin, CreateView):
    context_object_name = 'subscription_product'
    form_class = SubscriptionProductCreationForm
    http_method_names = ['get','post']
    model = SubscriptionProduct
    template_name = 'create/subscription-product-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Subscription Product created'
    
    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        subscription_product_name = cleaned_data.get('name')
        subscription_product_description = cleaned_data.get('description')
        subscription_product_active = cleaned_data.get('active')
        try:
            stripe_product = stripe.Product.create(
                name = subscription_product_name,
                description = subscription_product_description,
                active = subscription_product_active
            )
        except Exception as e:
            form.add_error(None, 'Something wrong happened. Please try again!')
        else:
            form.instance.id = stripe_product.id
        return super().form_valid(form)

class SubscriptionProductImageCreate(OnlineMaidStaffRequiredMixin,
                                SuccessMessageMixin, CreateView):
    context_object_name = 'subscription_product_image'
    form_class = SubscriptionProductImageCreationForm
    http_method_names = ['get','post']
    model = SubscriptionProductImage
    template_name = 'create/subscription-product-image-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Subscription Product Image created'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'subscription_product_id': self.kwargs.get(
                self.pk_url_kwarg
            )
        })
        return kwargs
    
class SubscriptionProductPriceCreate(OnlineMaidStaffRequiredMixin,
                                SuccessMessageMixin, CreateView):
    context_object_name = 'subscription_product_price'
    form_class = SubscriptionProductPriceCreationForm
    http_method_names = ['get','post']
    model = SubscriptionProductPrice
    template_name = 'create/subscription-product-price-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Subscription Product Price created'
    
    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        subscription_product = SubscriptionProduct.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )  
        )
        try:
            stripe_product = stripe.Product.retrieve(
                subscription_product.pk
            )
        except Exception as e:
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
                    active = subscription_product_active,
                    product = stripe_product.id
                )
            except Exception as e:
                form.add_error(
                    None,
                    _('Something wrong happened. Please try again!')
                )
            else:
                form.instance.id = stripe_price.id
                form.instance.subscription_product = subscription_product
        return super().form_valid(form)
    
# Delete Views
class SubscriptionProductImageDelete(OnlineMaidStaffRequiredMixin,
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
                subscription_product = self.object
            )
        ]
        try:
            stripe.Product.modify(
                self.object.pk,
                images = product_images
            )
        except Exception as e:
            print(e)
            
        return super().delete(request, *args, **kwargs)
    
# Generic Views
class CheckoutSession(View):
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types = ['card'],
                mode = 'subscription',
                line_items = [
                    {
                        'price': i
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
                status = 400
            )
            
class StripeWebhookView(View):
    http_method_names = ['post']
    endpoint_secret = 'whsec_7VRZrfVz3dwOCo49n2uLdIyibwXpOdeo'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)
        else:
            if event.type=='invoice.payment_failed':
                print(event)
            return HttpResponse(status=200)
