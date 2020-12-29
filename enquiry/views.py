# Imports from django
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, RedirectView
from django.views.generic.edit import CreateView

# Imports from project-wide files

# Imports from foreign installed apps
from accounts.models import Employer
from accounts.mixins import PotentialEmployerRequiredMixin

# Imports from local app
from .forms import EnquiryForm
from .models import Enquiry

# Start of Views

# Form Views
class EnquiryView(PotentialEmployerRequiredMixin, CreateView):
    context_object_name = 'enquiry'
    form_class = EnquiryForm
    http_method_names = ['get', 'post']
    model = Enquiry
    template_name = 'enquiry.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.employer = Employer.objects.get(
            user = self.request.user
        )
        return super().form_valid(form)

# Redirect Views
class DeactivateEnquiryView(PotentialEmployerRequiredMixin, RedirectView):
    http_method_names = ['get']
    pattern_name = None

    def get_redirect_url(self, *args, **kwargs):
        try:
            selected_enquiry = Enquiry.objects.get(
                pk = kwargs.get(
                    self.pk_url_kwarg
                ),
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
class EnquiryListView(PotentialEmployerRequiredMixin, ListView):
    context_object_name = 'enquiries'
    http_method_names = ['get']
    model = Enquiry
    template_name = 'list/enquiry-list.html'

    def get_queryset(self):
        return Enquiry.objects.filter(
            employer__user = self.request.user,
            active = True
        )

# Detail Views

# Create Views

# Update Views

# Delete Views