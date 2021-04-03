# Imports from django
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

# Imports from project-wide files

# Imports from foreign installed apps
from agency.mixins import OnlineMaidStaffRequiredMixin
from agency.models import Agency
from enquiry.models import GeneralEnquiry
from payment.models import SubscriptionProduct
from maid.models import Maid
from maid.filters import MiniMaidFilter

# Imports from local app

# Start of Views

# Template Views
class HomeView(TemplateView):
    http_method_names = ['get']
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        kwargs.update({
            'filter': MiniMaidFilter()
        })
        return kwargs

class AboutUsView(TemplateView):
    http_method_names = ['get']
    template_name = 'about-us.html'

class ContactUsView(TemplateView):
    http_method_names = ['get']
    template_name = 'contact-us.html'

class TermsOfSerivceView(TemplateView):
    http_method_names = ['get']
    template_name = 'terms-of-service.html'

class PrivacyPolicyView(TemplateView):
    http_method_names = ['get']
    template_name = 'privacy-policy.html'
    
class HowItWorksView(TemplateView):
    http_method_names = ['get']
    template_name = 'how-it-works.html'

class FAQView(TemplateView):
    http_method_names = ['get']
    template_name = 'faq.html'

class AdminPanelView(OnlineMaidStaffRequiredMixin, ListView):
    http_method_names = ['get']
    template_name = 'admin-panel.html'
    model = Agency
    paginate_by = 50
    context_object_name = 'agencies'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'subscription_products': SubscriptionProduct.objects.all() 
        })
        return context

class AdminPanelEnquiryListView(OnlineMaidStaffRequiredMixin, ListView):
    http_method_names = ['get']
    template_name = 'admin-panel-enquiries.html'
    model = GeneralEnquiry
    paginate_by = 50
    context_object_name = 'enquiries'

class Error403View(TemplateView):
    http_method_names = ['get']
    template_name = '403.html'
    
class Error404View(TemplateView):
    http_method_names = ['get']
    template_name = '404.html'
    
class Error500View(TemplateView):
    http_method_names = ['get']
    template_name = '500.html'
    
class RobotsTxt(TemplateView):
    http_method_names = ['get']
    template_name = 'robots.txt'
    content_type='text/plain'

# Redirect Views

# List Views

# Detail Views

# Create Views

# Update Views

# Delete Views