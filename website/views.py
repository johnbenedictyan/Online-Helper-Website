# Imports from django
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

# Imports from project-wide files

# Imports from foreign installed apps

# Imports from local app

# Start of Views

# Template Views
class HomeView(TemplateView):
    http_method_names = ['get']
    template_name = 'home.html'

class AboutUsView(TemplateView):
    http_method_names = ['get']
    template_name = 'about-us.html'

class ContactUsView(TemplateView):
    http_method_names = ['get']
    template_name = 'contact-us.html'

class TermsOfSerivceView(TemplateView):
    http_method_names = ['get']
    template_name = 'terms-of-service.html'

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