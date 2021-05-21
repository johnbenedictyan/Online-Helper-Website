# Imports from python
import json
from datetime import datetime, timedelta

# Imports from django
from django.contrib import messages
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView, CreateView

# Imports from foreign installed apps
from agency.forms import (
    AgencyForm, AgencyUpdateForm, AgencyOpeningHoursForm, AgencyEmployeeForm
)
from agency.formsets import (
    AgencyBranchFormSetHelper, AgencyBranchFormSet
)
from agency.models import (
    Agency, AgencyEmployee, AgencyPlan, AgencyBranch, AgencyOpeningHours
)
from agency.mixins import (
    AgencyLoginRequiredMixin, AgencyOwnerRequiredMixin, GetAuthorityMixin
)
from employer_documentation.models import Employer
from enquiry.models import GeneralEnquiry
from maid.constants import MaidFoodPreferenceChoices, MaidFoodPreferenceChoices
from maid.forms import (
    MainMaidCreationForm, MaidForm, MaidLanguageSpokenForm, 
    MaidLanguagesAndFHPDRForm, MaidExperienceForm,
    MaidAboutFDWForm, MaidEmploymentHistoryForm
)
from maid.formsets import (
    MaidLoanTransactionFormSet, MaidLoanTransactionFormSetHelper,
    MaidEmploymentHistoryFormSet, MaidEmploymentHistoryFormSetHelper
)
from maid.mixins import FDWLimitMixin
from maid.models import (
    Maid, MaidFoodHandlingPreference, MaidDietaryRestriction, 
    MaidInfantChildCare, MaidElderlyCare, MaidDisabledCare, 
    MaidGeneralHousework, MaidCooking, MaidLanguageProficiency
)
from payment.models import Customer, Subscription
from onlinemaid.constants import AG_OWNERS, AG_ADMINS
from onlinemaid.mixins import ListFilteredMixin, SuccessMessageMixin
# Imports from local app
from .filters import DashboardMaidFilter, DashboardEmployerFilter

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
class DashboardMaidList(AgencyLoginRequiredMixin, GetAuthorityMixin, ListFilteredMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/new-dashboard-maid-list.html'
    filter_set = DashboardMaidFilter
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        kwargs.update({
            'order_by': self.request.GET.get('order-by')
        })
        return kwargs
    
    def get_queryset(self):
        order_by = self.request.GET.get('order-by')
        if order_by:
            if order_by == 'serialNo':
                order_by = 'id'
            elif order_by == '-serialNo':
                order_by = '-id'
            elif order_by == 'nationality':
                order_by = 'country_of_origin'
            elif order_by == '-nationality':
                order_by = '-country_of_origin'
            elif order_by == 'type':
                order_by = 'maid_type'
            elif order_by == '-type':
                order_by = '-maid_type'
            elif order_by == 'ppExpiry':
                order_by = 'passport_expiry'
            elif order_by == '-ppExpiry':
                order_by = '-passport_expiry'
            elif order_by == 'dateCreated':
                order_by = 'created_on'
            elif order_by == '-dateCreated':
                order_by = '-created_on'
            return Maid.objects.filter(
                agency__pk = self.agency_id
            ).order_by(order_by)
        else:
            return Maid.objects.filter(
                agency__pk = self.agency_id
            ).order_by('passport_expiry')

class DashboardAccountList(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                           ListView):
    context_object_name = 'accounts'
    http_method_names = ['get']
    model = AgencyEmployee
    template_name = 'list/new-dashboard-account-list.html'
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
    template_name = 'list/new-dashboard-agency-branch-list.html'
    authority = ''
    agency_id = ''

    def get_queryset(self):
        return AgencyBranch.objects.filter(
            agency__pk = self.agency_id
        )
        
class DashboardCaseList(AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'cases'
    http_method_names = ['get']
    template_name = 'list/dashboard-case-list.html'
    authority = ''
    agency_id = ''

    def get_queryset(self):
        pass

class DashboardSalesList(AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'sales'
    http_method_names = ['get']
    template_name = 'list/dashboard-sales-list.html'
    authority = ''
    agency_id = ''

    def get_queryset(self):
        pass

class DashboardEmployerList(AgencyLoginRequiredMixin, GetAuthorityMixin, ListFilteredMixin, ListView):
    context_object_name = 'employers'
    http_method_names = ['get']
    model = Employer
    template_name = 'list/dashboard-employer-list.html'
    filter_set = DashboardEmployerFilter
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        kwargs.update({
            'order_by': self.request.GET.get('order-by')
        })
        return kwargs
    
    def get_queryset(self):
        order_by = self.request.GET.get('order-by')
        # if order_by:
        #     if order_by == 'serialNo':
        #         order_by = 'id'
        #     elif order_by == '-serialNo':
        #         order_by = '-id'
        #     elif order_by == 'employerName':
        #         order_by = 'country_of_origin'
        #     elif order_by == '-employerName':
        #         order_by = '-country_of_origin'
        #     elif order_by == 'dateOfBirth':
        #         order_by = 'maid_type'
        #     elif order_by == '-dateOfBirth':
        #         order_by = '-maid_type'
        #     elif order_by == 'eaPersonnel':
        #         order_by = 'passport_expiry'
        #     elif order_by == '-eaPersonnel':
        #         order_by = '-passport_expiry'
        #     return Employer.objects.filter(
        #         agency__pk = self.agency_id
        #     ).order_by(order_by)
        # else:
            # return Employer.objects.filter(
            #     agency__pk = self.agency_id
            # )
        return Employer.objects.all()

# Detail Views
class DashboardDetailView(AgencyLoginRequiredMixin, GetAuthorityMixin,
                            DetailView):
    http_method_names = ['get']
    authority = ''
    agency_id = ''
    
class DashboardAgencyDetail(DashboardDetailView):
    context_object_name = 'agency'
    model = Agency
    template_name = 'detail/new-dashboard-agency-detail.html'

    def get_object(self):
        agency = get_object_or_404(
            Agency, 
            pk=self.agency_id
        )
        return agency

class DashboardMaidDetail(DashboardDetailView):
    context_object_name = 'maid'
    model = Maid
    template_name = 'detail/new-dashboard-maid-detail.html'

    def get_object(self):
        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency__pk = self.agency_id
        )

class DashboardEmployerDetail(DashboardDetailView):
    context_object_name = 'employer'
    # model = Maid
    template_name = 'detail/new-dashboard-employer-detail.html'

    def get_object(self):
        pass
        # return Maid.objects.get(
        #     pk = self.kwargs.get(
        #         self.pk_url_kwarg
        #     ),
        #     agency__pk = self.agency_id
        # )

class DashboardCaseDetail(DashboardDetailView):
    context_object_name = 'case'
    # model = Maid
    template_name = 'detail/new-dashboard-case-detail.html'

    def get_object(self):
        pass
        # return Maid.objects.get(
        #     pk = self.kwargs.get(
        #         self.pk_url_kwarg
        #     ),
        #     agency__pk = self.agency_id
        # )

# Form Views
class DashboardMaidCreation(AgencyLoginRequiredMixin, GetAuthorityMixin,
                          FDWLimitMixin, SuccessMessageMixin, FormView):
    form_class = MainMaidCreationForm
    http_method_names = ['get','post']
    success_url = reverse_lazy('dashboard_maid_detail')
    template_name = 'form/maid-create-form.html'
    authority = ''
    agency_id = ''
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id,
            'update': False
        })
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            super().get_success_url(),
            kwargs={
                'pk':self.object.pk
            }
        )
    
    # def form_valid(self, form):
        # try:
        #     self.object = form.save()
        # except Exception as e:
        #     messages.warning(
        #         self.request,
        #         'Please try again',
        #         extra_tags='warning'
        #     )
        #     return super().form_invalid(form)
        # else:
        #     return super().form_valid(form)

class DashboardAgencyEmployeeEmployerReassignment(AgencyLoginRequiredMixin, 
                                                  GetAuthorityMixin,
                                                  SuccessMessageMixin, 
                                                  FormView):
    form_class = MainMaidCreationForm
    http_method_names = ['get','post']
    success_url = reverse_lazy('dashboard_maid_detail')
    template_name = 'form/maid-create-form.html'
    authority = ''
    agency_id = ''
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def form_valid(self, form):
        pass
    
class DashboardMaidSubFormView(AgencyLoginRequiredMixin, GetAuthorityMixin,
                               SuccessMessageMixin, FormView):
    http_method_names = ['get','post']
    pk_url_kwarg = 'pk'
    template_name = 'form/maid-create-form.html'
    authority = ''
    agency_id = ''
    maid_id = ''
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'maid_id': self.maid_id
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'maid_id': self.maid_id
        })
        return kwargs
    
    def get_initial(self):
        initial =  super().get_initial()
        self.maid_id = self.kwargs.get(
            self.pk_url_kwarg
        )
        return initial
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
class DashboardMaidLanguageSpokenFormView(DashboardMaidSubFormView):
    context_object_name = 'maid_languages'
    form_class = MaidLanguageSpokenForm
    success_message = 'Maid created'
    
    def get_initial(self):
        initial =  super().get_initial()
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        initial.update({
            'language_spoken': list(
                maid.languages.values_list(
                    'language',
                    flat=True
                )
            )
        })
        return initial
    
    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_maid_languages_and_fhpdr_update',
            kwargs={
                'pk':self.maid_id
            }
        )

class DashboardMaidLanguagesAndFHPDRFormView(DashboardMaidSubFormView):
    context_object_name = 'maid_food_handling_preference_dietary_restriction'
    form_class = MaidLanguagesAndFHPDRForm
    success_message = 'Maid created'

    def get_initial(self):
        initial =  super().get_initial()
        food_handling_pork = food_handling_beef = food_handling_veg = None
        dietary_restriction_pork = dietary_restriction_beef = None
        dietary_restriction_veg = None
        languages = None
        try:
            food_handling_pork = MaidFoodHandlingPreference.objects.get(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.PORK
            )
        except MaidFoodHandlingPreference.DoesNotExist:
            pass
        
        try:
            food_handling_pork = MaidFoodHandlingPreference.objects.get(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.BEEF
            )
        except MaidFoodHandlingPreference.DoesNotExist:
            pass
        
        try:
            food_handling_pork = MaidFoodHandlingPreference.objects.get(
                maid__pk=self.maid_id,
                preference=MaidFoodPreferenceChoices.VEG
            )
        except MaidFoodHandlingPreference.DoesNotExist:
            pass
        
        try:
            dietary_restriction_pork = MaidDietaryRestriction.objects.get(
                maid__pk=self.maid_id,
                restriction=MaidFoodPreferenceChoices.PORK
            )
        except MaidDietaryRestriction.DoesNotExist:
            pass
        
        try:
            dietary_restriction_beef = MaidDietaryRestriction.objects.get(
                maid__pk=self.maid_id,
                restriction=MaidFoodPreferenceChoices.BEEF
            )
        except MaidDietaryRestriction.DoesNotExist:
            pass
        
        try:
            dietary_restriction_veg = MaidDietaryRestriction.objects.get(
                maid__pk=self.maid_id,
                restriction=MaidFoodPreferenceChoices.VEG
            )
        except MaidDietaryRestriction.DoesNotExist:
            pass
            
        initial.update({
            'food_handling_pork': food_handling_pork,
            'food_handling_beef': food_handling_beef,
            'food_handling_veg': food_handling_veg,
            'dietary_restriction_pork': dietary_restriction_pork,
            'dietary_restriction_beef': dietary_restriction_beef,
            'dietary_restriction_veg': dietary_restriction_veg
        })
        
        try:
            languages = MaidLanguageProficiency.objects.get(
                maid__pk=self.maid_id
            )
        except MaidLanguageProficiency.DoesNotExist:
            pass
        finally:
            if languages:
                initial.update({
                    'english': languages.english,
                    'malay': languages.malay,
                    'mandarin': languages.mandarin,
                    'chinese_dialect': languages.chinese_dialect,
                    'hindi': languages.hindi,
                    'tamil': languages.tamil
                })
        return initial
    
    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_maid_experience_update',
            kwargs={
                'pk':self.maid_id
            }
        )

class DashboardMaidExperienceFormView(DashboardMaidSubFormView):
    context_object_name = 'maid_experience'
    form_class = MaidExperienceForm
    success_message = 'Maid created'
    
    def get_initial(self):
        initial =  super().get_initial()
        try:
            maid_cfi = MaidInfantChildCare.objects.get(
                maid__pk=self.maid_id
            )
        except:
            maid_cfi = {}

        try:
            maid_cfe = MaidElderlyCare.objects.get(
                maid__pk=self.maid_id
            )
        except:
            maid_cfe = {}

        try:
            maid_cfd = MaidDisabledCare.objects.get(
                maid__pk=self.maid_id
            )
        except:
            maid_cfd = {}

        try:
            maid_geh = MaidGeneralHousework.objects.get(
                maid__pk=self.maid_id
            )
        except:
            maid_geh = {}

        try:
            maid_cok = MaidCooking.objects.get(
                maid__pk=self.maid_id
            )
        except:
            maid_cok = {}

        initial.update({
            'cfi_assessment': maid_cfi.assessment,
            'cfi_willingness': maid_cfi.willingness,
            'cfi_experience': maid_cfi.experience,
            'cfi_remarks': maid_cfi.remarks,
            'cfi_other_remarks': maid_cfi.other_remarks,
            'cfe_assessment': maid_cfe.assessment,
            'cfe_willingness': maid_cfe.willingness,
            'cfe_experience': maid_cfe.experience,
            'cfe_remarks': maid_cfe.remarks,
            'cfe_other_remarks': maid_cfe.other_remarks,
            'cfd_assessment': maid_cfd.assessment,
            'cfd_willingness': maid_cfd.willingness,
            'cfd_experience': maid_cfd.experience,
            'cfd_remarks': maid_cfd.remarks,
            'cfd_other_remarks': maid_cfd.other_remarks,
            'geh_assessment': maid_geh.assessment,
            'geh_willingness': maid_geh.willingness,
            'geh_experience': maid_geh.experience,
            'geh_remarks': maid_geh.remarks,
            'geh_other_remarks': maid_geh.other_remarks,
            'cok_assessment': maid_cok.assessment,
            'cok_willingness': maid_cok.willingness,
            'cok_experience': maid_cok.experience,
            'cok_remarks': maid_cok.remarks,
            'cok_other_remarks': maid_cok.other_remarks
        })
        return initial
    
    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_maid_employment_history_update',
            kwargs={
                'pk':self.maid_id
            }
        )

class DashboardMaidAboutFDWFormView(DashboardMaidSubFormView):
    context_object_name = 'maid_about_me'
    form_class = MaidAboutFDWForm
    success_message = 'Maid created'

    def get_initial(self):
        initial =  super().get_initial()
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        initial.update({
            'about_me': maid.about_me
        })
        return initial
    
    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_maid_loan_update',
            kwargs={
                'pk':self.maid_id
            }
        )

class DashboardMaidLoanFormView(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                                SuccessMessageMixin, FormView):
    form_class = MaidLoanTransactionFormSet
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('dashboard_maid_list')
    template_name = 'form/maid-formset.html'
    pk_url_kwarg = 'pk'
    authority = ''
    agency_id = ''
    maid_id = ''
    success_message = 'Maid loan details updated'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'maid_id': self.maid_id
        })
        helper = MaidLoanTransactionFormSetHelper()
        # helper.add_input(
        #     Hidden(
        #         'submitFlag',
        #         'False',
        #         css_id="submitFlag"
        #     )
        # )
        helper.form_tag = False
        # helper.add_input(
        #     Button(
        #         "add",
        #         "Add Loan Transaction",
        #         css_class="btn btn-outline-primary w-50 mb-2 mx-auto",
        #         css_id="addOutletButton"
        #     )
        # )
        # helper.add_input(
        #     Submit(
        #         "save",
        #         "Save",
        #         css_class="btn btn-primary w-50 mb-2",
        #         css_id="submitButton"
        #     )
        # )
        context.update({
            'helper': helper
        })
        return context
    
    def get_formset_form_kwargs(self):
        self.maid_id = self.kwargs.get(
            self.pk_url_kwarg
        )
        kwargs = {
            'maid_id': self.maid_id
        }
        return kwargs

    def get_instance_object(self):
        return Maid.objects.get(
            pk=self.maid_id
        )
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.get_instance_object()
        })
        return kwargs
    
    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(
            form_kwargs=self.get_formset_form_kwargs(),
            **self.get_form_kwargs()
        )
        
    def form_valid(self, form):
        form.save()
        print(form.data)
        if form.data.get('submitFlag') == 'True':
            return super().form_valid(form)
        else:
            return HttpResponseRedirect(
                reverse_lazy(
                    'dashboard_maid_loan_update',
                    kwargs={
                        'pk':self.maid_id
                    }
                )
            )

class DashboardMaidEmploymentHistoryFormView(AgencyLoginRequiredMixin, 
                                             GetAuthorityMixin, 
                                             SuccessMessageMixin, FormView):
    form_class = MaidEmploymentHistoryFormSet
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('dashboard_maid_list')
    template_name = 'form/maid-formset.html'
    pk_url_kwarg = 'pk'
    authority = ''
    agency_id = ''
    maid_id = ''
    success_message = 'Maid employment history updated'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'maid_id': self.maid_id
        })
        helper = MaidEmploymentHistoryFormSetHelper()
        # helper.add_input(
        #     Hidden(
        #         'submitFlag',
        #         'False',
        #         css_id="submitFlag"
        #     )
        # )
        helper.form_tag = False
        # helper.add_input(
        #     Button(
        #         "add",
        #         "Add Employment History",
        #         css_class="btn btn-outline-primary w-50 mb-2 mx-auto",
        #         css_id="addButton"
        #     )
        # )
        # helper.add_input(
        #     Submit(
        #         "save",
        #         "Save",
        #         css_class="btn btn-primary w-50 mb-2",
        #         css_id="submitButton"
        #     )
        # )
        context.update({
            'helper': helper
        })
        return context
    
    def get_formset_form_kwargs(self):
        self.maid_id = self.kwargs.get(
            self.pk_url_kwarg
        )
        kwargs = {
            'maid_id': self.maid_id
        }
        return kwargs
    
    def get_instance_object(self):
        return Maid.objects.get(
            pk=self.maid_id
        )
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.get_instance_object()
        })
        return kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(
            form_kwargs=self.get_formset_form_kwargs(),
            **self.get_form_kwargs()
        )
        
    def form_valid(self, form):
        form.save()
        if form.data.get('submitFlag') == 'True':
            return super().form_valid(form)
        else:
            return HttpResponseRedirect(
                reverse_lazy(
                    'dashboard_maid_employment_history_update',
                    kwargs={
                        'pk':self.maid_id
                    }
                )
            )

    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_maid_about_fdw_update',
            kwargs={
                'pk':self.maid_id
            }
        )
        
class DashboardAgencyOutletDetailsFormView(AgencyLoginRequiredMixin,
                                           GetAuthorityMixin, 
                                           SuccessMessageMixin, FormView):
    form_class = AgencyBranchFormSet
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('dashboard_agency_opening_hours_update')
    template_name = 'update/dashboard-agency-outlet-details.html'
    authority = ''
    agency_id = ''
    success_message = 'Agency details updated'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        helper = AgencyBranchFormSetHelper()
        helper.form_tag = False
        # helper.add_input(
        #     Hidden(
        #         'submitFlag',
        #         'False',
        #         css_id="submitFlag"
        #     )
        # )
        # helper.add_input(
        #     Button(
        #         "add",
        #         "Add Outlet",
        #         css_class="btn btn-outline-primary w-50 mb-2",
        #         css_id="addButton"
        #     )
        # )
        # helper.add_input(
        #     Submit(
        #         "save",
        #         "Save",
        #         css_class="btn btn-primary w-50 mb-2",
        #         css_id="submitButton"
        #     )
        # )
        context.update({
            'helper': helper
        })
        return context
    
    def get_formset_form_kwargs(self):
        kwargs = {
            'agency_id': self.agency_id
        }
        return kwargs
    
    def get_instance_object(self):
        return Agency.objects.get(
            pk=self.agency_id
        )
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.get_instance_object()
        })
        return kwargs
    
    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(
            form_kwargs=self.get_formset_form_kwargs(),
            **self.get_form_kwargs()
        )
        
    def form_valid(self, form):
        form.save()
        if form.data.get('submitFlag') == 'True':
            return super().form_valid(form)
        else:
            return HttpResponseRedirect(
                reverse_lazy(
                    'dashboard_agency_outlet_details_update'
                )
            )
        
# Create Views
class DashboardCreateView(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                          SuccessMessageMixin, CreateView):
    http_method_names = ['get','post']
    authority = ''
    agency_id = ''
    
class DashboardMaidInformationCreate(DashboardCreateView):
    context_object_name = 'maid_information'
    form_class = MaidForm
    model = Maid
    template_name = 'form/maid-create-form.html'
    success_message = 'Maid created'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context.update({
            'new_maid': True
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id,
            'form_type': 'create'
        })
        return kwargs

    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_maid_language_spoken_update',
            kwargs={
                'pk':self.object.pk
            }
        )

class DashboardAgencyEmployeeCreate(DashboardCreateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeForm
    model = AgencyEmployee
    template_name = 'form/agency-employee-create-form.html'
    success_url = reverse_lazy('dashboard_account_list')
    success_message = 'Agency employee created'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id,
            'authority': self.authority,
            'form_type': 'create'
        })
        return kwargs

    def form_valid(self, form):
        agency = Agency.objects.get(
            pk = self.agency_id
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

# Update Views
class DashboardAgencyEmployeeUpdate(AgencyLoginRequiredMixin, 
                                    GetAuthorityMixin, SuccessMessageMixin, 
                                    UpdateView):
    context_object_name = 'agency_employee'
    form_class = AgencyEmployeeForm
    http_method_names = ['get','post']
    model = AgencyEmployee
    template_name = 'form/agency-employee-create-form.html'
    success_url = reverse_lazy('dashboard_account_list')
    success_message = 'Employee details updated'
    authority = ''
    agency_id = ''
    
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
        kwargs.update({
            'agency_id': self.agency_id,
            'authority': self.authority,
            'pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'form_type': 'update'
        })
        return kwargs

class DashboardAgencyUpdate(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                            SuccessMessageMixin, UpdateView):
    context_object_name = 'agency'
    form_class = AgencyForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'update/agency-details-form.html'
    success_url = reverse_lazy('dashboard_agency_detail')
    authority = ''
    agency_id = ''
    success_message = 'Agency details updated'

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.agency_id
    )
    
    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        branch_count = AgencyBranch.objects.filter(
            agency__pk=self.agency_id
        ).count()
        
        branch_1_display = 'd-none'
        branch_2_display = 'd-none'
        branch_3_display = 'd-none'
        branch_4_display = 'd-none'
        branch_5_display = 'd-none'
        
        if branch_count == 1:
            branch_1_display = ''
        elif branch_count == 2:
            branch_1_display = ''
            branch_2_display = ''
        elif branch_count == 3:
            branch_1_display = ''
            branch_2_display = ''
            branch_3_display = ''
        elif branch_count == 4:
            branch_1_display = ''
            branch_2_display = ''
            branch_3_display = ''
            branch_4_display = ''
        elif branch_count == 5:
            branch_1_display = ''
            branch_2_display = ''
            branch_3_display = ''
            branch_4_display = ''
            branch_5_display = ''
            
        branch_display_map = {
                'branch_1_display': branch_1_display,
                'branch_2_display': branch_2_display,
                'branch_3_display': branch_3_display,
                'branch_4_display': branch_4_display,
                'branch_5_display': branch_5_display
            }
        kwargs.update({
            'branch_display_map': branch_display_map,
            'agency_branch_row_number': branch_count
        })
        return kwargs
    
    def get_initial(self):
        initial =  super().get_initial()
        branch_list = AgencyBranch.objects.filter(
            agency__pk=self.agency_id
        )
        branch_count = branch_list.count()
        for index, element in enumerate(list(branch_list),1):
            initial[f'branch_{index}_name'] = element.name
            initial[f'branch_{index}_address_1'] = element.address_1
            initial[f'branch_{index}_address_2'] = element.address_2
            initial[f'branch_{index}_postal_code'] = element.postal_code
            initial[f'branch_{index}_email'] = element.email
            initial[f'branch_{index}_office_number'] = element.office_number
            initial[f'branch_{index}_mobile_number'] = element.mobile_number
            initial[f'branch_{index}_main'] = element.main_branch
            initial[f'branch_{index}_id'] = element.id
        
        opening_hours = AgencyOpeningHours.objects.get(
            agency__pk=self.agency_id
        )
        initial['opening_hours_type'] = opening_hours.type
        initial['opening_hours_monday'] = opening_hours.monday
        initial['opening_hours_tuesday'] = opening_hours.tuesday
        initial['opening_hours_wednesday'] = opening_hours.wednesday
        initial['opening_hours_thursday'] = opening_hours.thursday
        initial['opening_hours_friday'] = opening_hours.friday
        initial['opening_hours_saturday'] = opening_hours.saturday
        initial['opening_hours_sunday'] = opening_hours.sunday
        initial['opening_hours_public_holiday'] = opening_hours.public_holiday

        return initial

class DashboardAgencyInformationUpdate(AgencyLoginRequiredMixin, 
                                       GetAuthorityMixin, SuccessMessageMixin,
                                       UpdateView):
    context_object_name = 'agency'
    form_class = AgencyUpdateForm
    http_method_names = ['get','post']
    model = Agency
    template_name = 'update/dashboard-agency-update.html'
    success_url = reverse_lazy('dashboard_agency_detail')
    authority = ''
    agency_id = ''
    success_message = 'Agency details updated'

    def get_object(self, queryset=None):
        return Agency.objects.get(
            pk = self.agency_id
    )

class DashboardAgencyOpeningHoursUpdate(AgencyLoginRequiredMixin, 
                                       GetAuthorityMixin, SuccessMessageMixin,
                                       UpdateView):
    context_object_name = 'agency'
    form_class = AgencyOpeningHoursForm
    http_method_names = ['get','post']
    model = AgencyOpeningHours
    template_name = 'update/dashboard-agency-update.html'
    success_url = reverse_lazy('dashboard_agency_detail')
    authority = ''
    agency_id = ''
    success_message = 'Agency details updated'

    def get_object(self, queryset=None):
        return AgencyOpeningHours.objects.get(
            agency__pk = self.agency_id
    )

class DashboardMaidInformationUpdate(AgencyLoginRequiredMixin, 
                                       GetAuthorityMixin, SuccessMessageMixin,
                                       UpdateView):
    context_object_name = 'maid_information'
    form_class = MaidForm
    model = Maid
    template_name = 'form/maid-create-form.html'
    success_message = 'Maid updated'
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        self.maid_id = self.kwargs.get(
            self.pk_url_kwarg
        )
        context.update({
            'maid_id': self.maid_id,
            'new_maid': False
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id,
            'form_type': 'update'
        })
        return kwargs

    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_maid_languages_and_fhpdr_update',
            kwargs={
                'pk':self.object.pk
            }
        )
  
# Delete Views

# Generic Views
class DashboardDataProviderView(View):
    http_method_names = ['post']
    fake_data = [4568,1017,3950,3898,4364,4872,3052,4346,3884,3895,4316,1998,
                 4595,4887,4199,4518,2053,2862,3032,3752,1404,2432,3479,1108,
                 4673,2794,2890,4220,3562,3150,4128,1209,4668,2115,3094,4405,
                 3655,4254,3945,4958,3691,3850,3803,2049,2030,1851,4236,2602,
                 3161,2543,2292,3335,3732,2326,2074,1004,1258,2248,4442,4074,
                 4088,1440,2308,3257,3929,4497,3170,1454,2997,3198,4179,1393,
                 1340,1136,2356,2625,4167,3263,4235,3678,3805,4934,4806,4884,
                 1880,3598,4785,4945,1247,1463,4703,3296,1458,2785,3157,2845,
                 4158,2084,3649,3295,3246,3123,4413,4646,1278,2531,2218,3978,
                 2770,3458,3095,1289,4799,4390,2788,3549,3155,2940,2163,3355,
                 4158,3598]
    fake_sales_data = [1928.13,1654.01,1872.78,1912.47,1920.25,1223.21,1282.1,
                       1271.75,1696.94,1924.69,1261.49,1319.17,1807.36,1365.63,
                       1727.43,1055.6,1348.16,1568.3,1792.91,1294.07,1690.68,
                       1142.61,1853.0,1645.32,1341.31,1154.14,1798.84,1729.81,
                       1942.27,1202.71,1035.82,1017.09,1235.47,1190.02,1536.62,
                       1692.85,1335.03,1647.84,1867.06,1634.16,1718.82,1120.49,
                       1533.14,1355.13,1294.28,1397.56,1107.7,1736.71,1742.2,
                       1827.31,1141.72,1091.86,1359.71,1584.98,1700.06,1177.02,
                       1946.78,1732.02,1953.49,1260.4,1778.15,1561.59,1798.72,
                       1726.44,1290.43,1073.86,1132.2,1828.6,1045.69,1120.69,
                       1001.71,1377.45,1842.9,1371.19,1045.64,1810.85,1843.43,
                       1911.8,1604.64,1165.26,1148.73,1755.65,1409.31,1854.43,
                       1811.62,1212.29,1211.54,1640.7,1189.74,1107.42,1426.02,
                       1664.72,1917.44,1342.77,1019.53,1747.43,1369.28,1328.59,
                       1375.66,1186.99,1950.93,1446.33,1948.52,1120.59,1554.5,
                       1356.33,1725.75,1408.0,1674.73,1026.94,1518.31,1840.69,
                       1619.91,1855.73,1426.11,1964.36,1760.13,1126.69,1766.17,
                       1705.75]
    fake_cases_data = [16,12,8,6,11,5,6,9,3,1,3,13,8,5,6,12,2,17,2,10,4,12,5,
                       11,10,6,13,19,8,16,2,1,9,9,12,7,13,9,5,14,5,19,5,2,6,5,
                       9,5,17,4,16,17,12,6,18,19,6,12,2,13,2,7,9,5,2,10,6,11,
                       12,2,10,4,14,14,11,5,2,9,7,16,11,12,7,1,5,12,4,8,6,10,
                       11,12,5,13,4,18,13,13,5,9,9,18,7,9,15,7,20,11,9,12,4,13,
                       13,11,20,16,15,20,2,10]
    fake_branch_sales_data = [7203.69,8419.7,8230.95,9840.45,5877.32,7614.21,
                              7919.48,5403.54,6325.09,8116.59,6517.71,9828.19,
                              8632.35,5702.67,7274.22,8146.06,8446.57,9163.38,
                              5757.1,6281.02,6301.7,7759.16,7224.4,5220.92,
                              6322.76,6643.53,7529.99,6551.53,5120.07,8878.12,
                              9294.73,5194.74,8749.17,6188.3,8964.15,9950.87,
                              5056.55,7089.83,6415.79,7859.23,8783.14,9470.29,
                              8756.18,5328.67,7297.28,7814.36,5942.56,8052.46,
                              9640.71,9771.37,6753.69,7946.88,9562.48,9145.13,
                              5941.54,9267.76,9320.44,7578.25,9922.31,9648.36,
                              9222.82,5534.83,8289.89,8785.74,6196.33,7951.15,
                              5494.57,8937.8,9834.39,5595.87,8702.58,7737.33]
    fake_branch_sales_data_year = [11134.64,86113.64,81633.42,88957.0,77072.09,
                                   72969.25]
    fake_branch_cases_data = [78,72,78,79,93,52,51,100,67,65,70,88,78,76,71,50,
                              80,56,70,52,59,77,68,91,82,95,53,81,92,82,99,93,
                              76,84,67,52,79,66,76,88,75,95,99,84,51,92,81,71,
                              61,96,95,91,85,51,72,93,73,74,76,59,66,92,55,77,
                              60,85,65,64,62,85,70,75]
    fake_branch_cases_data_year = [127,49,13,81,110,113]
    fake_fdw_timline_data = [
        {
            "name":"Penny Truwert",
            "data": {
                "deposit_date":"07/04/2021",
                "apply_for_entry_approval_date":"11/04/2021",
                "arrival_date":"14/04/2021",
                "medical_checkup":"27/04/2021",
                "deployment_date":"04/05/2021",
                "thumbprint_date":"13/05/2021"
            }
        },
        {
            "name":"Alphard Hurry",
            "data": {
                "deposit_date":"07/04/2021",
                "apply_for_entry_approval_date":"14/04/2021",
                "arrival_date":"22/04/2021",
                "medical_checkup":"28/04/2021",
                "deployment_date":"04/05/2021",
                "thumbprint_date":"13/05/2021"
            }
        },
        {
            "name":"Goober Glascott",
            "data": {
                "deposit_date":"07/04/2021",
                "apply_for_entry_approval_date":"14/04/2021",
                "arrival_date":"22/04/2021",
                "medical_checkup":"27/04/2021",
                "deployment_date":"05/05/2021",
                "thumbprint_date":"11/05/2021"
            }
        },
        {
            "name":"Sanford Mum",
            "data": {
                "deposit_date":"06/04/2021",
                "apply_for_entry_approval_date":"14/04/2021",
                "arrival_date":"21/04/2021",
                "medical_checkup":"29/04/2021",
                "deployment_date":"04/05/2021",
                "thumbprint_date":"12/05/2021"
            }
        },
        {
            "name":"Adolph Slesser",
            "data": {
                "deposit_date":"06/04/2021",
                "apply_for_entry_approval_date":"13/04/2021",
                "arrival_date":"22/04/2021",
                "medical_checkup":"27/04/2021",
                "deployment_date":"06/05/2021",
                "thumbprint_date":"11/05/2021"
            }
        },
        {
            "name":"Donall Causley",
            "data": {
                "deposit_date":"07/04/2021",
                "apply_for_entry_approval_date":"15/04/2021",
                "arrival_date":"20/04/2021",
                "medical_checkup":"27/04/2021",
                "deployment_date":"04/05/2021",
                "thumbprint_date":"13/05/2021"
            }
        },
        {
            "name":"Marika Salmon",
            "data": {
                "deposit_date":"08/04/2021",
                "apply_for_entry_approval_date":"15/04/2021",
                "arrival_date":"21/04/2021",
                "medical_checkup":"27/04/2021",
                "deployment_date":"05/05/2021",
                "thumbprint_date":"11/05/2021"
            }
        },
        {
            "name":"Catha Pendrill",
            "data": {
                "deposit_date":"08/04/2021",
                "apply_for_entry_approval_date":"13/04/2021",
                "arrival_date":"21/04/2021",
                "medical_checkup":"29/04/2021",
                "deployment_date":"04/05/2021",
                "thumbprint_date":"12/05/2021"
            }
        },
        {
            "name":"Waring Ohrtmann",
            "data": {
                "deposit_date":"06/04/2021",
                "apply_for_entry_approval_date":"15/04/2021",
                "arrival_date":"20/04/2021",
                "medical_checkup":"27/04/2021",
                "deployment_date":"05/05/2021",
                "thumbprint_date":"13/05/2021"
            }
        },
        {
            "name":"Mallorie Kigelman",
            "data": {
                "deposit_date":"07/04/2021",
                "apply_for_entry_approval_date":"14/04/2021",
                "arrival_date":"21/04/2021",
                "medical_checkup":"29/04/2021",
                "deployment_date":"05/05/2021",
                "thumbprint_date":"13/05/2021"
            }
        }
    ]
    
    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body.decode('utf-8'))
        chart = request_data.get('chart')
        authority = request_data.get('authority')
        if chart['name'] == 'salesChart':
            if chart['year'] == '2010':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[0:12]
                }]
            elif chart['year'] == '2011':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[12:24]
                }]
            elif chart['year'] == '2012':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[24:36]
                }]
            elif chart['year'] == '2013':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[36:48]
                }]
            elif chart['year'] == '2014':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[48:60]
                }]
            elif chart['year'] == '2015':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[60:72]
                }]
            elif chart['year'] == '2016':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[72:84]
                }]
            elif chart['year'] == '2017':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[84:96]
                }]
            elif chart['year'] == '2018':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[96:108]
                }]
            elif chart['year'] == '2019':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[108:120]
                }]
            else:
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[120:]
                }]
                
        if chart['name'] == 'salesStaffPerformanceSales':
            if chart['year'] == '2010':
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_sales_data[0:36:3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_sales_data[1:37:3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_sales_data[2:38:3]
                        }
                    ]
                
            elif chart['year'] == '2011':
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_sales_data[36:72:3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_sales_data[37:73:3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_sales_data[38:74:3]
                        }
                    ]
                    
            elif chart['year'] == '2012':
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_sales_data[72:108:3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_sales_data[73:109:3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_sales_data[74:110:3]
                        }
                    ]
                    
            else:
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_sales_data[108::3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_sales_data[109::3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_sales_data[110::3]
                        }
                    ]
                
        if chart['name'] == 'salesStaffPerformanceCases':
            if chart['year'] == '2010':
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_cases_data[0:36:3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_cases_data[1:37:3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_cases_data[2:38:3]
                        }
                    ]
                
            elif chart['year'] == '2011':
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_cases_data[36:72:3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_cases_data[37:73:3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_cases_data[38:74:3]
                        }
                    ]
                    
            elif chart['year'] == '2012':
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_cases_data[72:108:3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_cases_data[73:109:3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_cases_data[74:110:3]
                        }
                    ]
                    
            else:
                if chart['staff'] == 'john':
                    chart_data = [
                        {
                            'name': 'john',
                            'data': self.fake_cases_data[108::3]
                        }
                    ]
                elif chart['staff'] == 'jane':
                    chart_data = [
                        {
                            'name': 'jane',
                            'data': self.fake_cases_data[109::3]
                        }
                    ]
                elif chart['staff'] == 'dave':
                    chart_data = [
                        {
                            'name': 'dave',
                            'data': self.fake_cases_data[110::3]
                        }
                    ]
                
        if chart['name'] == 'branchPerformanceSales':
            if chart['group_by'] == 'Month':
                if chart['year'] == '2010':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_sales_data[0:36:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_sales_data[1:37:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_sales_data[2:38:3]
                        }
                    ]
                elif chart['year'] == '2011':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_sales_data[36:72:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_sales_data[37:73:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_sales_data[38:74:3]
                        }
                    ]
            else:
                chart_data = [
                    {
                        'name': 'branch 1',
                        'data': self.fake_branch_sales_data_year[0::3]
                    },
                    {
                        'name': 'branch 2',
                        'data': self.fake_branch_sales_data_year[1::3]
                    },
                    {
                        'name': 'branch 3',
                        'data': self.fake_branch_sales_data_year[2::3]
                    }
                ]
                
        if chart['name'] == 'branchPerformanceCases':
            if chart['group_by'] == 'Month':
                if chart['year'] == '2010':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_cases_data[0:36:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_cases_data[1:37:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_cases_data[2:38:3]
                        }
                    ]
                elif chart['year'] == '2011':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_cases_data[36:72:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_cases_data[37:73:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_cases_data[38:74:3]
                        }
                    ]
            else:
                chart_data = [
                    {
                        'name': 'branch 1',
                        'data': self.fake_branch_cases_data_year[0::3]
                    },
                    {
                        'name': 'branch 2',
                        'data': self.fake_branch_cases_data_year[1::3]
                    },
                    {
                        'name': 'branch 3',
                        'data': self.fake_branch_cases_data_year[2::3]
                    }
                ]
        
        if chart['name'] == 'agencyTimelinePerformance':
            chart_data = [
                {
                    'name': 'Deposit',
                    'data': [3]
                },
                {
                    'name': 'IPA Approval',
                    'data': [24]
                },
                {
                    'name': 'Date of Approved Entry Application',
                    'data': [1]
                }
            ]
        
        if chart['name'] == 'fdwTimeline':
            if chart['group_by'] == 'Week':
                chart_data = [
                    {
                        'name': i['name'],
                        'data': [
                            {
                                'x': k.replace('_',' ').title(),
                                'y': [
                                    datetime.strptime(v, '%d/%m/%Y'),
                                    datetime.strptime(v, '%d/%m/%Y') + 
                                    timedelta(days=1)
                                ]
                            } for k,v in i['data'].items() if (
                                datetime.now().isocalendar()[1] + 1 == datetime.strptime(v, '%d/%m/%Y').isocalendar()[1]
                            )
                        ]
                    } for i in self.fake_fdw_timline_data
                ]
            elif chart['group_by'] == 'Month':
                chart_data = [
                    {
                        'name': i['name'],
                        'data': [
                            {
                                'x': k.replace('_',' ').title(),
                                'y': [
                                    datetime.strptime(v, '%d/%m/%Y'),
                                    datetime.strptime(v, '%d/%m/%Y') + 
                                    timedelta(days=1)
                                ]
                            } for k,v in i['data'].items() if (
                                datetime.strptime(v, '%d/%m/%Y').isocalendar()[1] - datetime.now().isocalendar()[1] < 5
                            )
                        ]
                    } for i in self.fake_fdw_timline_data
                ]
            
        data = {
            'name': 'Sales',
            'data': chart_data
        }
        return JsonResponse(data, status=200)