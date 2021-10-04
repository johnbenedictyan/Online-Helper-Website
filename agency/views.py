from typing import Optional

from django.conf import settings
from django.db.models.query import QuerySet as QS
from django.http.response import HttpResponse as RES
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from onlinemaid.mixins import ListFilteredMixin, SuccessMessageMixin
from onlinemaid.types import T

from .filters import AgencyFilter
from .forms import AgencyForm, AgencyOwnerCreationForm, PotentialAgencyForm
from .mixins import GetAuthorityMixin, OMStaffRequiredMixin
from .models import Agency, AgencyOwner, PotentialAgency


class AgencyList(GetAuthorityMixin, ListFilteredMixin, ListView):
    context_object_name = 'agencies'
    http_method_names = ['get']
    model = Agency
    template_name = 'list/agency-list.html'
    queryset = Agency.objects.filter(active=True)
    filter_set = AgencyFilter
    paginate_by = settings.AGENCY_PAGINATE_BY
    ordering = ['name']
    authority = ''
    agency_id = ''


class AgencyDetail(DetailView):
    context_object_name = 'agency'
    http_method_names = ['get']
    model = Agency
    template_name = 'detail/agency-detail.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        try:
            pk = int(
                self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        except Exception:
            return get_object_or_404(
                Agency,
                name_url=self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        else:
            return get_object_or_404(
                Agency,
                pk=pk
            )


class AgencyCreate(OMStaffRequiredMixin, SuccessMessageMixin, CreateView):
    context_object_name = 'agency'
    form_class = AgencyForm
    http_method_names = ['get', 'post']
    model = Agency
    template_name = 'create/agency-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Agency created'


class AgencyOwnerCreate(OMStaffRequiredMixin, SuccessMessageMixin, CreateView):
    context_object_name = 'agency_owner'
    form_class = AgencyOwnerCreationForm
    http_method_names = ['get', 'post']
    model = AgencyOwner
    template_name = 'create/agency-owner-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Agency owner created'

    def form_valid(self, form) -> RES:
        form.instance.agency = Agency.objects.get(
            pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)


class AgencySignUp(SuccessMessageMixin, CreateView):
    context_object_name = 'potential_agency'
    form_class = PotentialAgencyForm
    http_method_names = ['get', 'post']
    model = PotentialAgency
    template_name = 'create/agency-sign-up.html'
    success_url = reverse_lazy('home')
    success_message = '''
        Your request has been submitted. We will get back to you shortly!'''
