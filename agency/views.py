# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps

# Imports from local app
from .forms import (
    AgencyCreationForm, AgencyBranchForm, AgencyEmployeeCreationForm,
    AgencyOperatingHoursForm, AgencyPlanForm, AgencyAdministratorCreationForm,
    AgencyManagerCreationForm, AgencyOwnerCreationForm
)

from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOperatingHours, AgencyPlan,
    AgencyAdministrator, AgencyManager, AgencyOwner
)

from .mixins import SuperUserRequiredMixin

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
class AgencyCreate(CreateView):
    context_object_name = 'agency'
    form_class = AgencyCreationForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'create/agency-create.html'
    success_url = reverse_lazy('home')

class AgencyOwnerCreate(SuperUserRequiredMixin, CreateView):
    context_object_name = 'agency_owner'
    form_class = AgencyOwnerCreationForm
    http_method_names = ['get','post']
    model = AgencyOwner
    template_name = 'create/agency-owner-create.html'
    success_url = reverse_lazy('home')

class AgencyEmployeeCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeCreationForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'create/agency-employee-create.html'
    success_url = reverse_lazy('dashboard_account_list')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # As only the owner should be able to create employee accounts
        try:
            Agency.objects.get(
                pk = self.request.user.pk
            )
        except Agency.DoesNotExist:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.request.user.pk
        })
        return kwargs

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.request.user.pk
        )
        return super().form_valid(form)

class AgencyManagerCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'agency_manager'
    form_class = AgencyManagerCreationForm
    http_method_names = ['get','post']
    model = AgencyManager
    template_name = 'create/agency-manager-create.html'
    success_url = reverse_lazy('dashboard_account_list')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # As only the owner should be able to create employee accounts
        try:
            Agency.objects.get(
                pk = self.request.user.pk
            )
        except Agency.DoesNotExist:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.request.user.pk
        })
        return kwargs

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.request.user.pk
        )
        return super().form_valid(form)

class AgencyAdministratorCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'agency_administrator'
    form_class = AgencyAdministratorCreationForm
    http_method_names = ['get','post']
    model = AgencyAdministrator
    template_name = 'create/agency-administrator-create.html'
    success_url = reverse_lazy('dashboard_account_list')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # As only the owner should be able to create employee accounts
        try:
            Agency.objects.get(
                pk = self.request.user.pk
            )
        except Agency.DoesNotExist:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.request.user.pk
        )
        return super().form_valid(form)

class AgencyPlanCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'agency_plan'
    form_class = AgencyPlanForm
    http_method_names = ['get','post']
    model = AgencyPlan
    template_name = 'create/agency-plan-create.html'
    success_url = reverse_lazy('')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # Only the owner should be able to create agency plan(Buy biodata space)
        if self.pk_url_kwarg == self.request.user.pk:
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)

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

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # As only the owner should be able to update agency details
        if self.pk_url_kwarg == self.request.user.pk:
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.request.user.pk
    )

class AgencyBranchUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_branch'
    form_class = AgencyBranchForm
    http_method_names = ['get','post']
    model = AgencyBranch
    template_name = 'update/agency-branch-update.html'
    success_url = reverse_lazy('')
    pk_url_kwarg = 'agency_id'

    def dispatch(self, request, *args, **kwargs):
        # Checks if the agency id is the same as the request user id
        # As only the owner should be able to update agency details
        if self.pk_url_kwarg == self.request.user.pk:
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)

class AgencyOperatingHoursUpdate(LoginRequiredMixin, UpdateView):
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
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return AgencyOperatingHours.objects.get(
            pk = self.request.user.pk
        )

class AgencyAdministratorUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_administrator'
    form_class = AgencyAdministratorCreationForm
    http_method_names = ['get','post']
    model = AgencyAdministrator
    template_name = 'update/agency-administrator-update.html'
    success_url = reverse_lazy('')
    authority_dict = {}

    def authority_checker(self):
        try:
            administrator = AgencyAdministrator.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        except AgencyAdministrator.DoesNotExist:
            pass
        else:
            # Checks if user is the owner
            if administrator.agency.pk == self.request.user.pk:
                authority = 'owner'

            # Checks if administrator details being updated is the user's own
            # details
            if administrator.user == self.request.user:
                authority = 'administrator'

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
        self.authority_dict = self.authority_checker()
        if self.authority_dict['valid'] == False:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'employee_authority': self.authority_dict['authority']
        })
        return kwargs

    def get_context_data(self, **kwargs):
        # Passes the authority to the template so that certain fields can be 
        # restricted based on who is editing the agency employee object.
        context = super().get_context_data(**kwargs)
        context.update({
            'employee_authority': self.authority_dict['authority']
        })
        return context

class AgencyEmployeeUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeCreationForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'update/agency-employee-update.html'
    success_url = reverse_lazy('')

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
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Passes the authority to the template so that certain fields can be 
        # restricted based on who is editing the agency employee object.
        context = super().get_context_data(**kwargs)
        context.update({
            'employee_authority': self.authority_checker().authority
        })
        return context

class AgencyManagerUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'agency_manager'
    form_class = AgencyManagerCreationForm
    http_method_names = ['get','post']
    model = AgencyManager
    template_name = 'update/agency-manager-update.html'
    success_url = reverse_lazy('')
    authority_dict = {}

    def authority_checker(self):
        authority = None
        try:
            manager = AgencyManager.objects.get(
                pk = self.pk_url_kwarg
            )
        except AgencyManager.DoesNotExist:
            pass
        else:
            # Checks if user is the owner
            if manager.agency == self.request.user.agency:
                authority = 'owner'

            # Checks if user is the agency's administrator
            if AgencyAdministrator.objects.get(
                pk = self.request.user.pk,
                agency = manager.agency
            ):
                authority = 'administrator'

            # Checks if the manager being updated is a manager
            if manager.user == self.request.user:
                authority = 'manager'

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
        # As only the owner/administrator and manager should be able to update
        # the managers details
        self.authority_dict = self.authority_checker()

        if self.authority_dict['valid'] == False:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Passes the authority to the template so that certain fields can be 
        # restricted based on who is editing the agency manager object.
        context = super().get_context_data(**kwargs)
        context.update({
            'employee_authority': self.authority_dict['authority']
        })
        return context

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

class AgencyAdministratorDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'agency_administrator'
    http_method_names = ['get','post']
    model = AgencyAdministrator
    template_name = 'agency-administrator-delete.html'
    success_url = reverse_lazy('')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the user is the agency owner of the administrator's agency
        # As only the owner should be able to delete administrator accounts
        if AgencyAdministrator.objects.get(
            pk = self.pk_url_kwarg
        ).agency != Agency.objects.get(
            pk = self.request.user.pk
        ):
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)

class AgencyEmployeeDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'agency_employee'
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'agency-employee-delete.html'
    success_url = reverse_lazy('')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the user is the agency owner of the employee's agency
        # As only the owner should be able to delete employee accounts
        if AgencyEmployee.objects.get(
            pk = self.pk_url_kwarg
        ).agency != Agency.objects.get(
            pk = self.request.user.pk
        ):
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)

class AgencyManagerDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'agency_manager'
    http_method_names = ['get','post']
    model = AgencyManager
    template_name = 'agency-manager-delete.html'
    success_url = reverse_lazy('')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the user is the agency owner of the manager's agency
        # As only the owner should be able to delete manager accounts
        if AgencyManager.objects.get(
            pk = self.pk_url_kwarg
        ).agency != Agency.objects.get(
            user = self.request.user
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

class AgencyPlanDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'agency_plan'
    http_method_names = ['get','post']
    model = AgencyPlan
    template_name = 'agency-plan-delete.html'
    success_url = reverse_lazy('')

    def dispatch(self, request, *args, **kwargs):
        # Checks if the user is the agency owner 
        # As only the owner should be able to delete agency plans (biodata
        # subscriptions)
        if AgencyPlan.objects.get(
            pk = self.pk_url_kwarg
        ).agency != Agency.objects.get(
            pk = self.request.user.pk
        ):
            return self.handle_no_permission(request)
        return super().dispatch(request, *args, **kwargs)