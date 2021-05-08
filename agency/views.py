# Imports from django
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView, FormView
)

# Imports from foreign installed apps
import stripe
from extra_views import InlineFormSetView, InlineFormSetFactory, UpdateWithInlinesView
from onlinemaid.mixins import ListFilteredMixin, SuccessMessageMixin
from crispy_forms.layout import Submit

# Imports from local app
from .filters import AgencyFilter

from .forms import (
    AgencyForm, AgencyBranchForm, AgencyEmployeeForm,
    AgencyOpeningHoursForm, AgencyPlanForm, AgencyOwnerCreationForm,
    AgencyEmployeeForm, PotentialAgencyForm, AgencyUpdateForm
)

from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOpeningHours, AgencyPlan,
    AgencyOwner, PotentialAgency
)

from .mixins import (
    OnlineMaidStaffRequiredMixin, AgencyOwnerRequiredMixin, 
    SpecificAgencyOwnerRequiredMixin, SpecificAgencyEmployeeLoginRequiredMixin,
    GetAuthorityMixin
)

# Start of Views

# Template Views

# Redirect Views

# List Views
class AgencyList(ListFilteredMixin, ListView):
    context_object_name = 'agencies'
    http_method_names = ['get']
    model = Agency
    template_name = 'list/agency-list.html'
    queryset = Agency.objects.filter(active=True)
    filter_set = AgencyFilter
    paginate_by = settings.AGENCY_PAGINATE_BY
    ordering = ['name']

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
class AgencyCreate(OnlineMaidStaffRequiredMixin, SuccessMessageMixin,
                   CreateView):
    context_object_name = 'agency'
    form_class = AgencyForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'create/agency-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Agency created'

class AgencyOwnerCreate(OnlineMaidStaffRequiredMixin, SuccessMessageMixin,
                        CreateView):
    context_object_name = 'agency_owner'
    form_class = AgencyOwnerCreationForm
    http_method_names = ['get','post']
    model = AgencyOwner
    template_name = 'create/agency-owner-create.html'
    success_url = reverse_lazy('admin_panel')
    success_message = 'Agency owner created'

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

class AgencyEmployeeCreate(AgencyOwnerRequiredMixin, SuccessMessageMixin,
                           CreateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'create/agency-employee-create.html'
    success_url = reverse_lazy('dashboard_account_list')
    success_message = 'Agency employee created'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.request.user.agency_owner.agency.pk,
            'form_type': 'create'
        })
        return kwargs

    def form_valid(self, form):
        agency = Agency.objects.get(
            pk = self.request.user.agency_owner.agency.pk
        )
        form.instance.agency = agency
        if agency.amount_of_employees < agency.amount_of_employees_allowed:
            return super().form_valid(form)
        else:
            messages.warning(
                self.request,
                'You have reached the limit of employee accounts',
                extra_tags='error'
            )
            return super().form_invalid(form)

class AgencySignUp(SuccessMessageMixin, CreateView):
    context_object_name = 'potential_agency'
    form_class = PotentialAgencyForm
    http_method_names = ['get','post']
    model = PotentialAgency
    template_name = 'create/agency-sign-up.html'
    success_url = reverse_lazy('home')
    success_message = '''
        Your request has been submitted. We will get back to you shortly!'''

# Update Views
class AgencyUpdate(AgencyOwnerRequiredMixin, GetAuthorityMixin, 
                   SuccessMessageMixin, UpdateView):
    context_object_name = 'agency'
    form_class = AgencyUpdateForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'update/agency-update.html'
    success_url = reverse_lazy('dashboard_agency_detail')
    authority = ''
    agency_id = ''
    success_message = 'Agency details updated'

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.agency_id
    )

class AgencyBranchUpdate(SpecificAgencyOwnerRequiredMixin, GetAuthorityMixin,
                         SuccessMessageMixin, UpdateView):
    context_object_name = 'agency_branch'
    form_class = AgencyBranchForm
    http_method_names = ['get','post']
    model = AgencyBranch
    template_name = 'update/agency-branch-update.html'
    success_url = reverse_lazy('dashboard_branches_list')
    check_type = 'branch'
    authority = ''
    agency_id = ''
    form_type = 'UPDATE'
    success_message = 'Agency branch details updated'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id,
            'form_type': self.form_type
        })
        return kwargs

# class BranchInline(InlineFormSetFactory):
#     model = AgencyBranch
#     form_class = AgencyBranchForm
#     fields = '__all__'
#     # initial = [{'name': 'example1'}, {'name', 'example2'}]
#     # prefix = 'item-form'
#     factory_kwargs = {'extra': 1, 'max_num': None,
#                       'can_order': False, 'can_delete': False}
#     # formset_kwargs = {'auto_id': 'my_id_%s'}
    
class AgencyBranchFormSetView(GetAuthorityMixin, UpdateWithInlinesView):
    pass
#     model = Agency
#     inlines = [BranchInline]
#     template_name = 'update/agency-branch-formset.html'
#     fields = '__all__'
#     authority = ''
#     agency_id = ''
    
#     def get_object(self, queryset=None):
#         return Agency.objects.get(
#             pk=self.agency_id
#         )
        
#     model = Agency
#     template_name = 'update/agency-branch-formset.html'
#     authority = ''
#     agency_id = ''

#     def get_context_data(self, **kwargs):
#         self.object = self.get_object()
#         context = super().get_context_data(**kwargs)

#         helper = AgencyBranchFormSetHelper()
#         helper.add_input(Submit("submit", "Save"))

#         if self.request.POST:
#             context['formset'] = AgencyBranchFormSet(
#                 self.request.POST,
#                 instance=self.object
#             )
#             context['helper'] = helper
#         else:
#             context['formset'] = AgencyBranchFormSet(
#                 instance=self.object
#             )
#             context['helper'] = helper
#         return context

#     def get_object(self, queryset=None):
#         return Agency.objects.get(
#             pk=self.agency_id
#         )
    
#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return super().get(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return super().post(request, *args, **kwargs)

#     def get_form(self, form_class=None):
#         return AgencyBranchFormSet(
#             **self.get_form_kwargs(), 
#             instance=self.object
#         )

#     def form_valid(self, form):
#         form.save()

#         messages.add_message(
#             self.request,
#             messages.SUCCESS,
#             'Changes were saved.'
#         )

#         return self.get_success_url()

#     def get_success_url(self):
#         return HttpResponseRedirect(
#             reverse_lazy(
#                 'maid_employment_formset', 
#                 kwargs={'pk':self.object.pk}
#             )
#         )
        
class AgencyOpeningHoursUpdate(AgencyOwnerRequiredMixin, GetAuthorityMixin,
                                 SuccessMessageMixin, UpdateView):
    context_object_name = 'agency_opening_hours'
    form_class = AgencyOpeningHoursForm
    http_method_names = ['get','post']
    model = AgencyOpeningHours
    template_name = 'update/agency-operating-hours-update.html'
    success_url = reverse_lazy('dashboard_agency_detail')
    authority = ''
    agency_id = ''
    success_message = 'Agency operating hours updated'

    def get_object(self, queryset=None):
        return AgencyOpeningHours.objects.get(
            agency__pk = self.agency_id
        )

class AgencyEmployeeUpdate(SpecificAgencyEmployeeLoginRequiredMixin,
                           SuccessMessageMixin, UpdateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'update/agency-employee-update.html'
    success_url = reverse_lazy('dashboard_account_list')
    success_message = 'Employee details updated'

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
            'authority':authority,
            'form_type': 'update'
        })
        return kwargs








# Views that are going to be deprecated
class AgencyBranchCreate(AgencyOwnerRequiredMixin, GetAuthorityMixin,
                         SuccessMessageMixin, CreateView):
    pass
    # context_object_name = 'agency_branch'
    # form_class = AgencyBranchForm
    # http_method_names = ['get','post']
    # model = AgencyBranch
    # template_name = 'create/agency-branch-create.html'
    # success_url = reverse_lazy('dashboard_branches_list')
    # check_type = 'branch'
    # authority = ''
    # agency_id = ''
    # form_type = 'CREATE'
    # success_message = 'Agency branch created'

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({
    #         'agency_id': self.agency_id,
    #         'form_type': self.form_type
    #     })
    #     return kwargs
    
class AgencyPlanCreate(AgencyOwnerRequiredMixin, SuccessMessageMixin,
                       CreateView):
    pass
    # context_object_name = 'agency_plan'
    # form_class = AgencyPlanForm
    # http_method_names = ['get','post']
    # model = AgencyPlan
    # template_name = 'create/agency-plan-create.html'
    # success_url = reverse_lazy('')
    # success_message = 'Agency plan subscribed'

    # def post(self, request, *args, **kwargs):
    #     """
    #     Handle POST requests: instantiate a form instance with the passed
    #     POST variables and then check if it's valid.
    #     """
    #     form = self.get_form()
    #     if form.is_valid():
    #         # SOME PAYMENT LOGIC
    #         # IF PASS
    #         return self.form_valid(form)
    #         # ELSE
    #         # Return some valid payment page
    #     else:
    #         return self.form_invalid(form)

    # def form_valid(self, form):
    #     form.instance.agency = Agency.objects.get(
    #         pk = self.request.user.agency.pk
    #     )
    #     return super().form_valid(form)
    
class AgencyPlanUpdate(SpecificAgencyOwnerRequiredMixin, UpdateView):
    pass
    # context_object_name = 'agency_plan'
    # http_method_names = ['get','post']
    # model = AgencyPlan
    # template_name = 'update/agency-plan-update.html'
    # success_url = reverse_lazy('')
    # check_type = 'plan'
    # Do we want to allow users to 'upgrade' their plans
    
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

class AgencyEmployeeDelete(SpecificAgencyOwnerRequiredMixin, 
                           SuccessMessageMixin, DeleteView):
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

class AgencyPlanDelete(SpecificAgencyOwnerRequiredMixin, SuccessMessageMixin,
                       DeleteView):
    pass              
#     context_object_name = 'agency_plan'
#     http_method_names = ['post']
#     model = AgencyPlan
#     success_url = reverse_lazy('dashboard_agency_plan_list')
#     check_type = 'plan'
#     success_message = 'Agency plan unsubscribed'
    
class AgencyBranchDelete(SpecificAgencyOwnerRequiredMixin, GetAuthorityMixin,
                         SuccessMessageMixin, DeleteView):
    pass               
#     context_object_name = 'agency_branch'
#     http_method_names = ['post']
#     model = AgencyBranch
#     success_url = reverse_lazy('dashboard_branches_list')
#     check_type = 'branch'
#     authority = ''
#     agency_id = ''
#     success_message = 'Agency branch deleted'