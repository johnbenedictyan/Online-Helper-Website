# Imports from django
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

# Imports from project-wide files

# Imports from foreign installed apps
from accounts.models import PotentialEmployer
from accounts.mixins import PotentialEmployerRequiredMixin
from agency.mixins import OnlineMaidStaffRequiredMixin
from agency.models import Agency
from maid.models import Maid
from onlinemaid.mixins import SuccessMessageMixin

# Imports from local app
from .forms import GeneralEnquiryForm, AgencyEnquiryForm
from .models import GeneralEnquiry, AgencyEnquiry

# Start of Views

# Form Views
class GeneralEnquiryView(SuccessMessageMixin, CreateView):
    context_object_name = 'general_enquiry'
    form_class = GeneralEnquiryForm
    http_method_names = ['get', 'post']
    model = GeneralEnquiry
    template_name = 'general_enquiry.html'
    success_url = reverse_lazy('home')
    success_message = 'General Enquiry created'

    def form_valid(self, form):
        if self.request.user:
            form.instance.potential_employer = PotentialEmployer.objects.get(
                user = self.request.user
            )
        return super().form_valid(form)

class AgencyEnquiryView(SuccessMessageMixin, CreateView):
    context_object_name = 'agency_enquiry'
    form_class = AgencyEnquiryForm
    http_method_names = ['post']
    model = AgencyEnquiry
    template_name = 'general_enquiry.html'
    success_url = reverse_lazy('home')
    success_message = 'Enquiry created'

    def form_valid(self, form):
        if self.request.user:
            form.instance.agency = Agency.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        return super().form_valid(form)

class MaidEnquiryView(SuccessMessageMixin, CreateView):
    context_object_name = 'general_enquiry'
    form_class = GeneralEnquiryForm
    http_method_names = ['post']
    model = GeneralEnquiry
    template_name = 'general_enquiry.html'
    success_url = reverse_lazy('home')
    success_message = 'Enquiry created'

    def form_valid(self, form):
        if self.request.user:
            form.instance.potential_employer = PotentialEmployer.objects.get(
                user = self.request.user
            )
            form.instance.maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        return super().form_valid(form)


# Redirect Views
class DeactivateGeneralEnquiryView(PotentialEmployerRequiredMixin,
                                   RedirectView):
    http_method_names = ['get']
    pattern_name = None
    pk_url_kwarg = 'pk'	

    def get_redirect_url(self, *args, **kwargs):
        try:
            selected_enquiry = GeneralEnquiry.objects.get(
                pk = kwargs.get(
                    self.pk_url_kwarg
                ),
                active = True
            )
        except GeneralEnquiry.DoesNotExist:
            messages.error(
                self.request,
                'This enquiry does not exist'
            )
        else:
            if selected_enquiry.potential_employer == PotentialEmployer.objects.get(
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

class ToggleApproveEnquiryView(OnlineMaidStaffRequiredMixin, RedirectView):
    http_method_names = ['get']
    pattern_name = 'admin_panel_enquiry_list'
    pk_url_kwarg = 'pk'	

    def get_redirect_url(self, *args, **kwargs):
        try:
            selected_enquiry = GeneralEnquiry.objects.get(
                pk = kwargs.get(
                    self.pk_url_kwarg
                ),
                active = True
            )
        except GeneralEnquiry.DoesNotExist:
            messages.error(
                self.request,
                'This enquiry does not exist'
            )
        else:
            selected_enquiry.approved = not selected_enquiry.approved
            selected_enquiry.last_modified = request.user
            selected_enquiry.save()
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

# List Views
class EnquiryListView(PotentialEmployerRequiredMixin, ListView):
    context_object_name = 'enquiries'
    http_method_names = ['get']
    model = GeneralEnquiry
    template_name = 'list/enquiry-list.html'

    def get_queryset(self):
        return GeneralEnquiry.objects.filter(
            employer__user = self.request.user,
            active = True
        )

# Detail Views

# Create Views

# Update Views

# Delete Views

# Template Views
class SuccessfulEnquiryView(TemplateView):
    http_method_names = ['get']
    template_name = 'successful-enquiry.html'