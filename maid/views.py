# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from project-wide files
from onlinemaid.mixins import ListFilteredMixin, SuccessMessageMixin

# Imports from foreign installed apps
from agency.models import Agency
from agency.mixins import AgencyLoginRequiredMixin, GetAuthorityMixin

# Imports from local app
from .filters import MaidFilter
from .mixins import (
    SpecificAgencyMaidLoginRequiredMixin, SpecificAgencyOwnerRequiredMixin
)

from .forms import (
    MaidCreationForm, MaidBiodataForm, MaidFamilyDetailsForm, 
    MaidInfantChildCareForm, MaidElderlyCareForm, MaidDisabledCareForm,
    MaidGeneralHouseworkForm, MaidCookingForm, MaidFoodHandlingPreferenceForm,
    MaidDietaryRestrictionForm, MaidEmploymentHistoryForm,
    MaidUpdateForm
)

from .models import (
    Maid, MaidBiodata, MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare,
    MaidDisabledCare, MaidGeneralHousework, MaidCooking, 
    MaidFoodHandlingPreference, MaidDietaryRestriction, MaidEmploymentHistory,
    MaidAgencyFeeTransaction
)

from .mixins import SpecificAgencyMaidLoginRequiredMixin

# Start of Views

# Template Views

# Redirect Views
class MaidTogglePublished(SpecificAgencyMaidLoginRequiredMixin, RedirectView):
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        try:
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        except Maid.DoesNotExist:
            messages.error(
                self.request,
                'This maid does not exist'
            )
        else:
            maid.published = not maid.published
            maid.save()
            kwargs.pop(self.pk_url_kwarg)
        finally:
            return reverse_lazy(
                'dashboard_maid_list'
            )
        
# List Views
class MaidList(ListFilteredMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    queryset = Maid.objects.filter(published=True)
    template_name = 'list/maid-list.html'
    filter_set = MaidFilter

class MaidEmploymentHistoryList(AgencyLoginRequiredMixin, ListView):
    context_object_name = 'maid_employment_history_list'
    http_method_names = ['get']
    model = MaidEmploymentHistory
    template_name = 'list/maid-employment-history-list.html'

    def get_queryset(self):
        return MaidEmploymentHistory.objects.filter(
            maid__pk = self.kwargs['maid_id'],
            maid__agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

# Detail Views
class MaidDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'maid'
    http_method_names = ['get']
    model = Maid
    template_name = 'detail/maid-detail.html'
    
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        similar_maids = Maid.objects.filter(
            biodata__country_of_origin=self.object.biodata.country_of_origin,
            responsibilities=self.object.get_main_responsibility(),
            biodata__languages__in=self.object.biodata.languages.all()
        ).exclude(
            pk=self.object.pk
        ).distinct()
        kwargs.update({
            'similar_maids': similar_maids
        })
        return kwargs

# Create Views
class MaidCreate(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                 SuccessMessageMixin, CreateView):
    context_object_name = 'maid'
    form_class = MaidCreationForm
    http_method_names = ['get','post']
    model = Maid
    template_name = 'create/maid-create.html'
    success_url = reverse_lazy('dashboard_maid_detail')
    authority = ''
    agency_id = ''
    success_message = 'FDW Biodata created'

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk=self.agency_id
        )
        initial_agency_fee_amount = form.cleaned_data.get(
            'initial_agency_fee_amount'
        )
        initial_agency_fee_description = form.cleaned_data.get(
            'initial_agency_fee_description'
        )
        response = super().form_valid(form)
        MaidBiodata.objects.create(
            maid=self.object
        )
        MaidFamilyDetails.objects.create(
            maid=self.object
        )
        MaidInfantChildCare.objects.create(
            maid=self.object
        )
        MaidElderlyCare.objects.create(
            maid=self.object
        )
        MaidDisabledCare.objects.create(
            maid=self.object
        )
        MaidGeneralHousework.objects.create(
            maid=self.object
        )
        MaidCooking.objects.create(
            maid=self.object
        )
        MaidAgencyFeeTransaction.objects.create(
            maid=self.object,
            amount=initial_agency_fee_amount,
            transaction_type='ADD',
            description=initial_agency_fee_description
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id
        })
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk':self.object.pk
            }
        )

class MaidFoodHandlingPreferenceCreate(AgencyLoginRequiredMixin, 
                                       SuccessMessageMixin, CreateView):
    context_object_name = 'maid_food_handling_preference'
    form_class = MaidFoodHandlingPreferenceForm
    http_method_names = ['get','post']
    model = MaidFoodHandlingPreference
    template_name = 'create/maid-food-handling-preference-create.html'
    success_url = reverse_lazy('')
    success_message = 'Maid food handling preference created'

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

class MaidDietaryRestrictionCreate(AgencyLoginRequiredMixin, 
                                   SuccessMessageMixin, CreateView):
    context_object_name = 'maid_dietary_restriction'
    form_class = MaidDietaryRestrictionForm
    http_method_names = ['get','post']
    model = MaidDietaryRestriction
    template_name = 'create/maid-dietary-restriction-create.html'
    success_url = reverse_lazy('')
    success_message = 'Maid dietary restriction created'

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

class MaidEmploymentHistoryCreate(AgencyLoginRequiredMixin,
                                  SuccessMessageMixin, CreateView):
    context_object_name = 'maid_employment_history'
    form_class = MaidEmploymentHistoryForm
    http_method_names = ['get','post']
    model = MaidEmploymentHistory
    template_name = 'create/maid-employment-history-create.html'
    success_url = reverse_lazy('')
    success_message = 'Maid employment history created'

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

# Update Views
class MaidUpdate(SpecificAgencyMaidLoginRequiredMixin, GetAuthorityMixin,
                 SuccessMessageMixin, UpdateView):
    context_object_name = 'maid'
    form_class = MaidUpdateForm
    http_method_names = ['get','post']
    model = Maid
    template_name = 'update/maid-update.html'
    success_message = 'Maid details updated'
    authority = ''
    agency_id = ''

    def get_object(self, queryset=None):
        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency__pk = self.agency_id
        )

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidBiodataUpdate(SpecificAgencyMaidLoginRequiredMixin, 
                        SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_biodata'
    form_class = MaidBiodataForm
    http_method_names = ['get','post']
    model = MaidBiodata
    template_name = 'update/maid-biodata-update.html'
    success_message = 'FDW biodata updated'

    def get_object(self, queryset=None):
        return MaidBiodata.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidFamilyDetailsUpdate(SpecificAgencyMaidLoginRequiredMixin, 
                              SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_family_details'
    form_class = MaidFamilyDetailsForm
    http_method_names = ['get','post']
    model = MaidFamilyDetails
    template_name = 'update/maid-family-details-update.html'
    success_message = 'Maid family details updated'

    def get_object(self, queryset=None):
        return MaidFamilyDetails.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidInfantChildCareUpdate(
    SpecificAgencyMaidLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_infant_child_care'
    form_class = MaidInfantChildCareForm
    http_method_names = ['get','post']
    model = MaidInfantChildCare
    template_name = 'update/maid-infant-child-care-update.html'
    success_message = 'Maid infant child care information updated'

    def get_object(self, queryset=None):
        return MaidInfantChildCare.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidElderlyCareUpdate(SpecificAgencyMaidLoginRequiredMixin,
                            SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_elderly_care'
    form_class = MaidElderlyCareForm
    http_method_names = ['get','post']
    model = MaidElderlyCare
    template_name = 'update/maid-elderly-care-update.html'
    success_message = 'Maid elderly care information updated'

    def get_object(self, queryset=None):
        return MaidElderlyCare.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidDisabledCareUpdate(SpecificAgencyMaidLoginRequiredMixin,
                             SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_disabled_care'
    form_class = MaidDisabledCareForm
    http_method_names = ['get','post']
    model = MaidDisabledCare
    template_name = 'update/maid-disabled-care-update.html'
    success_message = 'Maid disabled care information updated'

    def get_object(self, queryset=None):
        return MaidDisabledCare.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidGeneralHouseworkUpdate(SpecificAgencyMaidLoginRequiredMixin,
                                 SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_general_housework'
    form_class = MaidGeneralHouseworkForm
    http_method_names = ['get','post']
    model = MaidGeneralHousework
    template_name = 'update/maid-general-housework-update.html'
    success_message = 'Maid general housework care information updated'

    def get_object(self, queryset=None):
        return MaidGeneralHousework.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidCookingUpdate(SpecificAgencyMaidLoginRequiredMixin,
                        SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_cooking'
    form_class = MaidCookingForm
    http_method_names = ['get','post']
    model = MaidCooking
    template_name = 'update/maid-cooking-update.html'
    success_message = 'Maid cooking care information updated'

    def get_object(self, queryset=None):
        return MaidCooking.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidEmploymentHistoryUpdate(SpecificAgencyMaidLoginRequiredMixin,
                                  SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_employment_history'
    form_class = MaidEmploymentHistoryForm
    http_method_names = ['get','post']
    model = MaidEmploymentHistory
    template_name = 'update/maid-employment-history-update.html'
    success_url = reverse_lazy('')
    success_message = 'Maid employment history updated'

    def get_object(self, queryset=None):
        return MaidEmploymentHistory.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            maid__agency = self.request.user.agency_owner.agency
        )

# Delete Views
class MaidDelete(SpecificAgencyOwnerRequiredMixin, SuccessMessageMixin,
                 DeleteView):
    context_object_name = 'maid'
    http_method_names = ['post']
    model = Maid
    success_url = reverse_lazy('')
    check_type = 'maid'
    success_message = 'Maid deleted'

    def get_object(self, queryset=None):
        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency = self.request.user.agency_owner.agency
        )

class MaidFoodHandlingPreferenceDelete(SpecificAgencyOwnerRequiredMixin,
                                       SuccessMessageMixin, DeleteView):
    context_object_name = 'maid_food_handling_preference'
    http_method_names = ['post']
    model = MaidFoodHandlingPreference
    success_url = reverse_lazy('')
    check_type = 'maid'
    success_message = 'Maid food handling information deleted'

class MaidDietaryRestrictionDelete(SpecificAgencyOwnerRequiredMixin,
                                   SuccessMessageMixin, DeleteView):
    context_object_name = 'maid_dietary_restriction'
    http_method_names = ['post']
    model = MaidDietaryRestriction
    success_url = reverse_lazy('')
    check_type = 'maid'
    success_message = 'Maid dietary restriction deleted'

class MaidEmploymentHistoryDelete(SpecificAgencyOwnerRequiredMixin,
                                  SuccessMessageMixin, DeleteView):
    context_object_name = 'maid_employment_history'
    http_method_names = ['post']
    model = MaidEmploymentHistory
    success_url = reverse_lazy('')
    check_type = 'maid'
    success_message = 'Maid employment history deleted'

    def get_object(self, queryset=None):
        return MaidEmploymentHistory.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            maid__agency = self.request.user.agency_owner.agency
        )

# Generic Views
class MaidProfileView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        try:
            selected_maid = Maid.objects.get(
                pk = self.kwargs.get('pk')
            )
        except Maid.DoesNotExist:
            data = {
                'error': 'Maid does not exist'
            }
            return JsonResponse(data, status=404)
        else:
            data = {
                'salary': selected_maid.salary,
                'days_off': selected_maid.days_off,
                'employment_history': [
                    {
                        'start_date': eh.start_date,
                        'end_date': eh.end_date,
                        'country': eh.country,
                        'work_duration': eh.work_duration,
                        'work_duties': [
                            work_duty for work_duty in eh.work_duties
                        ]
                    } for eh in selected_maid.employment_history.all()
                ]
            }
            return JsonResponse(data, status=200)