# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps

# Imports from local app
from .forms import (
    AgencyCreationForm, AgencyBranchForm, AgencyEmployeeCreationForm,
    AgencyOperatingHoursForm, AgencyPlanForm, AgencyOwnerCreationForm,
    AgencyEmployeeUpdateForm
)

from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOperatingHours, AgencyPlan,
    AgencyOwner
)

from .mixins import (
    OnlineMaidStaffRequiredMixin, AgencyOwnerRequiredMixin, 
    AgencyAdministratorRequiredMixin, AgencyManagerRequiredMixin,
    AgencyAdminTeamRequiredMixin, AgencySalesTeamRequiredMixin,
    AgencyLoginRequiredMixin, SpecificAgencyOwnerRequiredMixin,
    SpecificAgencyEmployeeLoginRequiredMixin
)

# Start of Views

# Template Views

# Redirect Views

# List Views
class AgencyList(ListView):
    context_object_name = 'agencies'
    http_method_names = ['get']
    model = Agency
    template_name = 'list/agency-list.html'

# Detail Views
class AgencyDetail(DetailView):
    context_object_name = 'agency'
    http_method_names = ['get']
    model = Agency
    template_name = 'detail/agency-detail.html'

    def get_object(self):
        obj = super().get_object()
        # if obj.complete == False:
        #     raise Http404

        return obj
    
# Create Views
class AgencyCreate(OnlineMaidStaffRequiredMixin, CreateView):
    context_object_name = 'agency'
    form_class = AgencyCreationForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'create/agency-create.html'
    success_url = reverse_lazy('admin_panel')

    def form_valid(self, form):
        response = super().form_valid(form)
        AgencyBranch.objects.create(
            agency=self.object
        )
        AgencyOperatingHours.objects.create(
            agency=self.object
        )

        return HttpResponseRedirect(self.get_success_url())

class AgencyOwnerCreate(OnlineMaidStaffRequiredMixin, CreateView):
    context_object_name = 'agency_owner'
    form_class = AgencyOwnerCreationForm
    http_method_names = ['get','post']
    model = AgencyOwner
    template_name = 'create/agency-owner-create.html'
    success_url = reverse_lazy('admin_panel')

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

class AgencyEmployeeCreate(AgencyOwnerRequiredMixin, CreateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeCreationForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'create/agency-employee-create.html'
    success_url = reverse_lazy('dashboard_account_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.request.user.agency_owner.agency.pk
        })
        return kwargs

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.request.user.agency_owner.agency.pk
        )
        return super().form_valid(form)

class AgencyPlanCreate(AgencyOwnerRequiredMixin, CreateView):
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

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.request.user.agency.pk
        )
        return super().form_valid(form)

# Update Views
class AgencyUpdate(AgencyOwnerRequiredMixin, UpdateView):
    context_object_name = 'agency'
    form_class = AgencyCreationForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'update/agency-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.request.user.agency.pk
    )

class AgencyBranchUpdate(SpecificAgencyOwnerRequiredMixin, UpdateView):
    context_object_name = 'agency_branch'
    form_class = AgencyBranchForm
    http_method_names = ['get','post']
    model = AgencyBranch
    template_name = 'update/agency-branch-update.html'
    success_url = reverse_lazy('')
    check_type = 'branch'

class AgencyOperatingHoursUpdate(AgencyOwnerRequiredMixin, UpdateView):
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

class AgencyEmployeeUpdate(SpecificAgencyEmployeeLoginRequiredMixin, UpdateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeUpdateForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'update/agency-employee-update.html'
    success_url = reverse_lazy('dashboard_account_list')

    def get_agency_id(self):
        if self.request.user.groups.filter(name='Agency Owners').exists():
            return self.request.user.agency_owner.agency.pk
        else:
            return self.request.user.agency_employee.agency.pk

    def get_initial(self):
        initial = super().get_initial()
        employee = AgencyEmployee.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        initial['email'] = employee.user.email

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.request.user.groups.filter(name='Agency Owners').exists():
            authority = 'employee'
        else:
            authority = 'owner'

        kwargs.update({
            'agency_id': self.get_agency_id(),
            'pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'authority':authority
        })
        return kwargs

class AgencyPlanUpdate(SpecificAgencyOwnerRequiredMixin, UpdateView):
    context_object_name = 'agency_plan'
    http_method_names = ['get','post']
    model = AgencyPlan
    template_name = 'update/agency-plan-update.html'
    success_url = reverse_lazy('')
    check_type = 'plan'
    # Do we want to allow users to 'upgrade' their plans

# Delete Views
class AgencyDelete(AgencyOwnerRequiredMixin, DeleteView):
    context_object_name = 'agency'
    http_method_names = ['post']
    model = Agency
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.request.user.pk
        )

class AgencyEmployeeDelete(SpecificAgencyOwnerRequiredMixin, DeleteView):
    context_object_name = 'agency_employee'
    http_method_names = ['post']
    model = AgencyEmployee
    check_type = 'employee'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        # Executes the soft delete of the agency employee object so that the 
        # transaction history of the particular agency employee does not 
        # get deleted.
        self.object.deleted = True
        self.object.save()

        return HttpResponseRedirect(success_url)

class AgencyPlanDelete(SpecificAgencyOwnerRequiredMixin, DeleteView):
    context_object_name = 'agency_plan'
    http_method_names = ['post']
    model = AgencyPlan
    success_url = reverse_lazy('dashboard_agency_plan_list')
    check_type = 'plan'
