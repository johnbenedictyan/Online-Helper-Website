# Imports from django
from django.views.generic import FormView

# Imports from project-wide files

# Imports from foreign installed apps

# Imports from local app

# Start of Views

# Form Views
class GeneralEnquiryView(FormView):
    http_method_names = ['get', 'post']
    template_name = 'general-enquiry.html'

class SpecificEnquiryView(FormView):
    http_method_names = ['get', 'post']
    template_name = 'specific-enquiry.html'

# Redirect Views

# List Views

# Detail Views

# Create Views

# Update Views

# Delete Views