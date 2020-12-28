# Imports from django
from django.contrib import messages
from django.views.generic import FormView, ListView, RedirectView

# Imports from project-wide files

# Imports from foreign installed apps
from accounts.models import Employer

# Imports from local app
from .forms import EnquiryForm
from .models import Enquiry

# Start of Views

# Form Views
class EnquiryView(FormView):
    form_class = EnquiryForm
    http_method_names = ['get', 'post']
    template_name = 'enquiry.html'

# Redirect Views
class DeactivateEnquiryView(RedirectView):
    http_method_names = ['get']
    pattern_name = None

    def get_redirect_url(self, *args, **kwargs):
        try:
            selected_enquiry = Enquiry.objects.get(
                pk = kwargs.get('pk'),
                active = True
            )
        except Enquiry.DoesNotExist:
            messages.error(
                self.request,
                'This enquiry does not exist'
            )
        else:
            selected_enquiry.active = False
            selected_enquiry.save()
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

# List Views
class EnquiryListView(ListView):
    context_object_name = 'enquries'
    http_method_names = ['get']
    model = Enquiry
    template_name = 'list/enquiry-list.html'

    def get_queryset(self):
        return Enquiry.objects.filter(
            employer = Employer.objects.get(
                user = self.request.user
            ),
            active = True
        )

# Detail Views

# Create Views

# Update Views

# Delete Views