# Imports from python
from itertools import chain

# Imports from django
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps
from agency.models import Agency, AgencyEmployee, AgencyAdministrator
from maid.models import Maid

# Imports from local app

# Start of Views

# Template Views
class DashboardHomePage(LoginRequiredMixin, TemplateView):
    template_name = 'base/dashboard-home-page.html'

# Redirect Views

# List Views
class DashboardAccountList(LoginRequiredMixin, ListView):
    context_object_name = 'accounts'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/dashboard-account-list.html'

    def authority_checker(self):
        # Checks if user is the owner
        if self.pk_url_kwarg == self.request.user.pk:
            authority = 'owner'

        # Checks if user is the agency's administrator
        if AgencyAdministrator.objects.get(
            pk = self.request.user.pk,
            agency = Agency.objects.get(
                pk = self.pk_url_kwarg
            )
        ):
            authority = 'administrator'

        if authority:
            valid = True
        else:
            valid = False

        authority_dict = {
            'valid': valid,
            'authority': authority
        }

    def dispatch(self, request, *args, **kwargs):
        if self.authority_checker().valid == False:
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return chain(
            AgencyAdministrator.objects.filter(
                agency = Agency.objects.get(
                    pk = self.pk_url_kwarg
                )
            ),
            AgencyEmployee.objects.filter(
                agency = Agency.objects.get(
                    pk = self.pk_url_kwarg
                )
            )
        )

    def get_context_data(self, **kwargs):
        # Passes the authority to the template so that certain fields can be 
        # restricted based on who is editing the agency employee object.
        context = super().get_context_data(**kwargs)
        context.update({
            'employee_authority': self.authority_checker().authority
        })
        return context

class DashboardMaidList(ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/dashboard-maid-list.html'
    pk_url_kwarg = 'pk'

    def authority_checker(self):
        authority = None

        agency = Agency.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )

        # Checks if user is the owner
        if self.kwargs.get(
            self.pk_url_kwarg
        ) == self.request.user.pk:
            authority = 'owner'

        # Checks if user is the agency's administrator
        try:
            agency_administrator = AgencyAdministrator.objects.get(
                pk = self.request.user.pk,
                agency = agency
            )
        except AgencyAdministrator.DoesNotExist:
            pass
        else:
            authority = 'administrator'

        # Checks if the employee being updated is an employee
            try:
                employee = AgencyEmployee.objects.get(
                    pk = self.request.user.pk,
                    agency = agency
                )
            except AgencyEmployee.DoesNotExist:
                pass
            else:
                # Checks if user is the employee's branch manager
                if employee.role == 'M':
                    authority = 'manager'
                else:
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
        if not request.user.is_authenticated:
            raise PermissionDenied()

        if self.authority_checker()['valid'] == False:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Maid.objects.filter(
            agency = Agency.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )

    def get_context_data(self, **kwargs):
        # Passes the authority to the template so that certain fields can be 
        # restricted based on who is editing the agency employee object.
        context = super().get_context_data(**kwargs)
        context.update({
            'employee_authority': self.authority_checker()['authority']
        })
        return context

# Detail Views

# Create Views

# Update Views

# Delete Views
