# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps

# Imports from local app
from .forms import (
    AgencyCreationForm, AgencyContactInformationForm, AgencyLocationForm,
    AgencyEmployeeCreationForm, AgencyOperatingHoursForm, AgencyPlanForm
)

from .models import (
    Agency, AgencyContactInformation, AgencyEmployee, AgencyLocation, 
    AgencyOperatingHours, AgencyPlan
)

# Start of Views

# Template Views

# Redirect Views

# List Views
class AgencyList(ListView):
    context_object_name = 'agency'
    http_method_names = ['get']
    model = Agency
    template_name = 'list/agency-list.html'

# Detail Views
class AgencyDetail(DetailView):
    context_object_name = 'agency'
    http_method_names = ['get']
    model = Agency
    template_name = 'detail/agency-detail.html'
    
# Create Views
class AgencyCreate(CreateView):
    context_object_name = 'agency'
    form_class = AgencyCreationForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'create/agency-create.html'
    success_url = reverse_lazy('home')

class AgencyEmployeeCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeCreationForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'create/agency-employee-create.html'
    success_url = reverse_lazy('')

class AgencyPlanCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'agency_plan'
    form_class = AgencyPlanForm
    http_method_names = ['get','post']
    model = AgencyPlan
    template_name = 'create/agency-plan-create.html'
    success_url = reverse_lazy('')

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            # SOME PAYMENT LOGIC
            # IF PASS
            return self.form_valid(form)
            # ELSE
            # Return some valid payment page
        else:
            return self.form_invalid(form)

# Update Views
class AgencyUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency'
    form_class = AgencyCreationForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'update/agency-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.request.user.pk
    )

class AgencyContactInformationUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_contact_information'
    form_class = AgencyContactInformationForm
    http_method_names = ['get','post']
    model = AgencyContactInformation
    template_name = 'update/agency-contact-information-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return AgencyContactInformation.objects.get(
            pk = self.request.user.pk
        )

class AgencyLocationUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_location'
    form_class = AgencyLocationForm
    http_method_names = ['get','post']
    model = AgencyLocation
    template_name = 'update/agency-location-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return AgencyLocation.objects.get(
            pk = self.request.user.pk
        )

class AgencyOperatingHoursUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_operating_hours'
    form_class = AgencyOperatingHoursForm
    http_method_names = ['get','post']
    model = AgencyOperatingHours
    template_name = 'update/agency-operating-hours-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return AgencyOperatingHours.objects.get(
            pk = self.request.user.pk
        )

class AgencyEmployeeUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeCreationForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'update/agency-employee-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.request.user.pk
        )

class AgencyPlanUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_plan'
    http_method_names = ['get','post']
    model = AgencyPlan
    template_name = 'update/agency-plan-update.html'
    success_url = reverse_lazy('')
    # Do we want to allow users to 'upgrade' their plans

# Delete Views
class AgencyDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'agency'
    http_method_names = ['get','post']
    model = Agency
    template_name = 'agency-delete.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.request.user.pk
        )

class AgencyEmployeeDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'agency_employee'
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'agency-employee-delete.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return AgencyEmployee.objects.get(
            pk = self.pk_url_kwarg,
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

class AgencyPlanDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'agency_plan'
    http_method_names = ['get','post']
    model = AgencyPlan
    template_name = 'agency-plan-delete.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return AgencyPlan.objects.get(
            pk = self.kwargs.pk_url_kwarg,
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )