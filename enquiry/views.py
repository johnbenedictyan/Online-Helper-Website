# Imports from django
from django.views.generic import FormView

# Imports from project-wide files

# Imports from foreign installed apps

# Imports from local app
from .forms import EnquiryForm

# Start of Views

# Form Views
class EnquiryView(FormView):
    form_class = EnquiryForm
    http_method_names = ['get', 'post']
    template_name = 'enquiry.html'

# Redirect Views

# List Views

# Detail Views

# Create Views

# Update Views

# Delete Views