# Imports from django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView

# Imports from project-wide files

# Imports from foreign installed apps
import stripe
from agency.mixins import AgencyOwnerRequiredMixin, GetAuthorityMixin

# Imports from local app
from .models import Invoice, Customer

# Start of Views

# Template Views

# Redirect Views
class CustomerPortal(AgencyOwnerRequiredMixin, GetAuthorityMixin,
                     RedirectView):
    authority = ''
    agency_id = ''
    
    def get_redirect_url(self, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer_id = Customer.objects.get(
            agency__pk=self.agency_id
        ).stripe_customer_id
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=self.request.build_absolute_uri(
                reverse_lazy('dashboard_home')
            ),
        )
        return session.url
    
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