# Imports from python
from itertools import chain

# Imports from django
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps
from accounts.models import Employer
from agency.models import Agency, AgencyEmployee, AgencyPlan
from agency.mixins import (
    AgencyLoginRequiredMixin, AgencyOwnerRequiredMixin, GetAuthorityMixin
)
from enquiry.models import Enquiry
from maid.models import Maid

# Imports from local app

# Start of Views

# Template Views
class DashboardHomePage(AgencyLoginRequiredMixin, TemplateView):
    template_name = 'base/dashboard-home-page.html'

# Redirect Views

# List Views
class DashboardMaidList(AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/dashboard-maid-list.html'
    authority = ''

    def get_queryset(self):
        if self.authority == 'owner':
            agency = self.request.user.agency_owner.agency
        else:
            agency = self.request.user.agency_employee.agency
            
        return Maid.objects.filter(
            agency = agency
        )

class DashboardAccountList(
    AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'accounts'
    http_method_names = ['get']
    model = AgencyEmployee
    template_name = 'list/dashboard-account-list.html'
    authority = ''

    def get_queryset(self):
        if self.authority == 'owner':
            agency = self.request.user.agency_owner.agency
        else:
            agency = self.request.user.agency_employee.agency
            
        return AgencyEmployee.objects.filter(
            agency = agency
        )

class DashboardAgencyPlanList(AgencyOwnerRequiredMixin, ListView):
    context_object_name = 'plans'
    http_method_names = ['get']
    model = AgencyPlan
    template_name = 'list/dashboard-agency-plan-list.html'

class DashboardEnquiriesList(AgencyLoginRequiredMixin, ListView):
    context_object_name = 'enquiries'
    http_method_names = ['get']
    model = Enquiry
    template_name = 'list/dashboard-enquiry-list.html'

# Detail Views
class DashboardAgencyDetail(
    AgencyLoginRequiredMixin, GetAuthorityMixin, DetailView):
    context_object_name = 'agency'
    http_method_names = ['get']
    model = Agency
    template_name = 'detail/dashboard-agency-detail.html'
    authority = ''

    def get_object(self):
        if self.authority == 'owner':
            agency = self.request.user.agency_owner.agency
        else:
            agency = self.request.user.agency_employee.agency

        agency = get_object_or_404(Agency, pk=agency.pk)

        return agency

class DashboardMaidDetail(
    AgencyLoginRequiredMixin, GetAuthorityMixin, DetailView):
    context_object_name = 'maid'
    http_method_names = ['get']
    model = Maid
    template_name = 'detail/dashboard-maid-detail.html'
    authority = ''

    def get_object(self):
        if self.authority == 'owner':
            agency = self.request.user.agency_owner.agency
        else:
            agency = self.request.user.agency_employee.agency

        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency = agency
        )

# Create Views

# Update Views

# Delete Views
