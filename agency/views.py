# Django Imports
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView

# Project Apps Imports
from onlinemaid.mixins import ListFilteredMixin, SuccessMessageMixin

# App Imports
from .filters import AgencyFilter
from .forms import AgencyForm, AgencyOwnerCreationForm, PotentialAgencyForm
from .models import Agency, AgencyOwner, PotentialAgency
from .mixins import (
    GetAuthorityMixin, OMStaffRequiredMixin, AgencyOwnerRequiredMixin,
)

# Start of Views


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

    def get_queryset(self):
        try:
            pk = int(
                self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        except Exception:
            return Agency.objects.get(
                name_url=self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        else:
            return Agency.objects.get(
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

    def form_valid(self, form):
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


class AgencyDelete(AgencyOwnerRequiredMixin, SuccessMessageMixin, DeleteView):
    pass
#     context_object_name = 'agency'
#     http_method_names = ['post']
#     model = Agency
#     success_url = reverse_lazy('home')
#     success_message = 'Agency deleted'

#     def get_object(self, queryset=None):
#         return Agency.objects.get(
#             pk = self.request.user.pk
#         )


class AgencyEmployeeDelete(SuccessMessageMixin, DeleteView):
    pass
#     context_object_name = 'agency_employee'
#     http_method_names = ['post']
#     model = AgencyEmployee
#     check_type = 'employee'
#     success_message = 'Employee account deleted'

#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         success_url = self.get_success_url()

#         # Executes the soft delete of the agency employee object so that the
#         # transaction history of the particular agency employee does not
#         # get deleted.
#         self.object.deleted = True
#         self.object.save()

#         return HttpResponseRedirect(success_url)


class AgencyPlanDelete(SuccessMessageMixin, DeleteView):
    pass
#     context_object_name = 'agency_plan'
#     http_method_names = ['post']
#     model = AgencyPlan
#     success_url = reverse_lazy('dashboard_agency_plan_list')
#     check_type = 'plan'
#     success_message = 'Agency plan unsubscribed'
