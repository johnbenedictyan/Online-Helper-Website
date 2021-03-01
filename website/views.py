# Imports from python
from random import shuffle

# Imports from django
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

# Imports from project-wide files

# Imports from foreign installed apps
from agency.mixins import OnlineMaidStaffRequiredMixin
from agency.models import Agency
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
        featured_maids = Maid.objects.filter(
            featured=True
        )
        shuffle(featured_maids)
        kwargs.update({
            'filter': MiniMaidFilter(),
            'featured_maids': featured_maids
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

class AdminPanelView(OnlineMaidStaffRequiredMixin, TemplateView):
    http_method_names = ['get']
    template_name = 'admin-panel.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        kwargs.update({
            'agencies': Agency.objects.all(),
            'subscription_products': SubscriptionProduct.objects.all() 
        })
        return kwargs

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