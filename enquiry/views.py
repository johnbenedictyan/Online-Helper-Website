# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView, RedirectView

# Imports from project-wide files

# Imports from foreign installed apps
from accounts.models import Employer

# Imports from local app
from .forms import EnquiryForm
from .models import Enquiry

# Start of Views

# Form Views
class EnquiryView(LoginRequiredMixin, FormView):
    form_class = EnquiryForm
    http_method_names = ['get', 'post']
    template_name = 'enquiry.html'

# Redirect Views
class DeactivateEnquiryView(LoginRequiredMixin, RedirectView):
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
            if selected_enquiry.employer == Employer.objects.get(
                user = self.request.user
            ):
                selected_enquiry.active = False
                selected_enquiry.save()
            else:
                messages.error(
                    self.request,
                    'This enquiry does not exist'
                )
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

# List Views
class EnquiryListView(LoginRequiredMixin, ListView):
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