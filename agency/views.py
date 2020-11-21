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
    AgencyOperatingHoursForm, AgencyPlanForm, AgencyOwnerCreationForm
)

from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOperatingHours, AgencyPlan,
    AgencyOwner
)

from .mixins import (
    OnlineMaidStaffRequiredMixin, AgencyOwnerRequiredMixin, 
    AgencyAdministratorRequiredMixin, AgencyManagerRequiredMixin,
    AgencyAdminTeamRequiredMixin, AgencySalesTeamRequiredMixin,
    AgencyLoginRequiredMixin, SpecificAgencyOwnerRequiredMixin
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
    success_url = reverse_lazy('home')

class AgencyOwnerCreate(OnlineMaidStaffRequiredMixin, CreateView):
    context_object_name = 'agency_owner'
    form_class = AgencyOwnerCreationForm
    http_method_names = ['get','post']
    model = AgencyOwner
    template_name = 'create/agency-owner-create.html'
    success_url = reverse_lazy('home')

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
            'agency_id': self.request.user.agency.pk
        })
        return kwargs

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.request.user.agency.pk
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
    pk_url_kwarg = 'agency_id'

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # As only the owner should be able to update agency details
        if self.pk_url_kwarg == self.request.user.pk:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return AgencyOperatingHours.objects.get(
            pk = self.request.user.pk
        )

class AgencyEmployeeUpdate(SpecificAgencyOwnerRequiredMixin, UpdateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeCreationForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'update/agency-employee-update.html'
    success_url = reverse_lazy('')
    check_type = 'employee'

    def authority_checker(self):
        authority = None
        try:
            employee = AgencyEmployee.objects.get(
                pk = self.pk_url_kwarg
            )
        except AgencyEmployee.DoesNotExist:
            pass
        else:
            # Checks if user is the owner
            if employee.agency.pk == self.request.user.pk:
                authority = 'owner'

            # Checks if user is the agency's administrator
            if AgencyAdministrator.objects.get(
                pk = self.request.user.pk,
                agency = employee.agency
            ):
                authority = 'administrator'

            # Checks if the employee being updated is a manager
            if employee.role == 'M':
                
                #Checks if the manager is trying to update their own details
                if employee.user == self.request.user:
                    authority = 'manager'

            # Else means that both managers from the same branch can 
            # edit sales staff's details
            else:
                # Checks if user is the employee's branch manager
                if AgencyEmployee.objects.get(
                    pk = self.request.user.pk,
                    branch = employee.branch
                ).role == 'M':
                    authority = 'manager'

                # Checks if user is the employee themselves
                if employee.user == self.request.user:
                    authority = 'employee'

            if authority:
                valid = True
            else:
                valid = False

            authority_dict = {
                'valid': valid,
                'authority': authority
            }

            return authority_dict

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # As only the owner/administrator and employee should be able to update
        # the employees details
        if self.authority_checker().valid == False:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Passes the authority to the template so that certain fields can be 
        # restricted based on who is editing the agency employee object.
        context = super().get_context_data(**kwargs)
        context.update({
            'employee_authority': self.authority_checker().authority
        })
        return context

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
    http_method_names = ['get','post']
    model = Agency
    template_name = 'agency-delete.html'
    success_url = reverse_lazy('')

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

    def dispatch(self, request, *args, **kwargs):
        # Checks if the user is the agency owner of the employee's agency
        # As only the owner should be able to delete employee accounts
        if AgencyEmployee.objects.get(
            pk = self.pk_url_kwarg
        ).agency != AgencyOwner.objects.get(
            pk = self.request.user.pk
        ).agency:
            raise PermissionDenied()
        else:
            return super().dispatch(request, *args, **kwargs)

class AgencyPlanDelete(SpecificAgencyOwnerRequiredMixin, DeleteView):
    context_object_name = 'agency_plan'
    http_method_names = ['get','post']
    model = AgencyPlan
    template_name = 'agency-plan-delete.html'
    success_url = reverse_lazy('')
    check_type = 'plan'

    def dispatch(self, request, *args, **kwargs):
        # Checks if the user is the agency owner 
        # As only the owner should be able to delete agency plans (biodata
        # subscriptions)
        if AgencyPlan.objects.get(
            pk = self.pk_url_kwarg
        ).agency != Agency.objects.get(
            pk = self.request.user.pk
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)