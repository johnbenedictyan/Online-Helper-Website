# Imports from python
from itertools import chain

# Imports from django
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps
from accounts.models import Employer
from agency.models import Agency, AgencyEmployee, AgencyPlan, AgencyBranch
from agency.mixins import (
    AgencyLoginRequiredMixin, AgencyOwnerRequiredMixin, GetAuthorityMixin
)
from enquiry.models import GeneralEnquiry
from maid.models import Maid
from payment.models import Customer, Subscription
from onlinemaid.constants import AG_OWNERS, AG_ADMINS

# Imports from local app

# Start of Views

# Template Views
class DashboardHomePage(AgencyLoginRequiredMixin, GetAuthorityMixin,
                        TemplateView):
    template_name = 'base/dashboard-home-page.html'
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        agency = Agency.objects.get(
            pk=self.agency_id
        )
        dashboard_home_page_kwargs = {
            'accounts': {
                'current': AgencyEmployee.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_employees_allowed
            },
            'biodata': {
                'current': Maid.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_biodata_allowed
            },
            'branches': {
                'current': AgencyBranch.objects.filter(
                    agency=agency
                ).count(),
                'max': None
            },
            'subscriptions': {
                'current': Subscription.objects.filter(
                    customer=Customer.objects.get(
                        agency=agency
                    )
                ).count(),
                'max': None
            },
            'employers': {
                'current': 123,
                'max': None
            },
            'sales': {
                'current': 123,
                'max': None
            },
            'enquiries': {
                'current': agency.get_enquiries().count(),
                'max': None
            }
        }
        kwargs.update(dashboard_home_page_kwargs)
        return kwargs

# Redirect Views

# List Views
class DashboardMaidList(AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/dashboard-maid-list.html'
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        agency = Agency.objects.get(
            pk=self.agency_id
        )
        kwargs.update({
            'biodata': {
                'current': Maid.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_biodata_allowed
            },
            'featured_maids': {
                'current': Maid.objects.filter(
                    agency=agency,
                    featured=True
                ).count(),
                'max': agency.amount_of_featured_biodata_allowed
            }
        })
        return kwargs
    
    def get_queryset(self):
        return Maid.objects.filter(
            agency__pk = self.agency_id
        ).order_by('id')

class DashboardAccountList(
    AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'accounts'
    http_method_names = ['get']
    model = AgencyEmployee
    template_name = 'list/dashboard-account-list.html'
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        agency = Agency.objects.get(
            pk=self.agency_id
        )
        kwargs.update({
            'employee_accounts': {
                'current': AgencyEmployee.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_employees_allowed
            }
        })
        return kwargs
    
    def get_queryset(self):
        if self.authority == AG_OWNERS or self.authority == AG_ADMINS:
            return AgencyEmployee.objects.filter(
                agency__pk = self.agency_id
            )
        else:
            return AgencyEmployee.objects.filter(
                agency__pk = self.agency_id,
                branch = self.request.user.agency_employee.branch
            )


class DashboardAgencyPlanList(AgencyOwnerRequiredMixin, ListView):
    context_object_name = 'plans'
    http_method_names = ['get']
    model = AgencyPlan
    template_name = 'list/dashboard-agency-plan-list.html'
    
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        dashboard_agency_plan_kwargs = {
        }
        kwargs.update(dashboard_agency_plan_kwargs)
        return kwargs

class DashboardEnquiriesList(AgencyLoginRequiredMixin, ListView):
    context_object_name = 'enquiries'
    http_method_names = ['get']
    model = GeneralEnquiry
    template_name = 'list/dashboard-enquiry-list.html'

class DashboardAgencyBranchList(AgencyLoginRequiredMixin, GetAuthorityMixin,
                                ListView):
    context_object_name = 'branches'
    http_method_names = ['get']
    model = AgencyBranch
    template_name = 'list/dashboard-agency-branch-list.html'
    authority = ''
    agency_id = ''

    def get_queryset(self):
        return AgencyBranch.objects.filter(
            agency__pk = self.agency_id
        )

# Detail Views
class DashboardAgencyDetail(AgencyLoginRequiredMixin, GetAuthorityMixin,
                            DetailView):
    context_object_name = 'agency'
    http_method_names = ['get']
    model = Agency
    template_name = 'detail/dashboard-agency-detail.html'
    authority = ''
    agency_id = ''

    def get_object(self):
        agency = get_object_or_404(Agency, pk=self.agency_id)
        return agency

class DashboardMaidDetail(AgencyLoginRequiredMixin, GetAuthorityMixin,
                          DetailView):
    context_object_name = 'maid'
    http_method_names = ['get']
    model = Maid
    template_name = 'detail/dashboard-maid-detail.html'
    authority = ''
    agency_id = ''

    def get_object(self):
        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency__pk = self.agency_id
        )

# Create Views

# Update Views

# Delete Views

# Generic Views
class DashboardDataProviderView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body.decode('utf-8'))
        model = request_data.get('model')
        fields = request_data.get('fields')
        data = {
        }
        return JsonResponse(data, status=200)