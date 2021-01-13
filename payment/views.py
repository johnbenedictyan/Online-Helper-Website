# Imports from modules
import json

# Imports from django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.urls.base import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView

# Imports from project-wide files

# Imports from foreign installed apps
import stripe
from stripe.api_resources import line_item, payment_method
from agency.mixins import AgencyOwnerRequiredMixin, GetAuthorityMixin

# Imports from local app
from .models import Invoice, Customer

# Start of Views

# Template Views
from django.http import JsonResponse

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

class CheckoutSucess(RedirectView):
    http_method_names = ['get']
    pattern_name = None
    
    def get_redirect_url(self, *args, **kwargs):
        messages.success(
            self.request,
            'Payment Sucessful',
            extra_tags='sucess'
        )
        return super().get_redirect_url()
    
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

# Detail Views
class InvoiceDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'invoice'
    http_method_names = ['get']
    model = Invoice
    template_name = 'invoice-detail.html'

# Create Views

# Delete Views

# Generic Views
class CheckoutSession(View):
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.data)
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types = ['card'],
                mode = 'subscription',
                line_items = [
                    {
                        'price': 'fake',
                        'quantity': 123
                    }
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