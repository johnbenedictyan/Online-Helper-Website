# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from project-wide files
from onlinemaid.mixins import ListFilteredMixin

# Imports from foreign installed apps
from agency.models import Agency

# Imports from local app
from .filters import MaidFilter

from .forms import (
    MaidCreationForm, MaidBiodataForm, MaidFamilyDetailsForm, 
    MaidInfantChildCareForm, MaidElderlyCareForm, MaidDisabledCareForm,
    MaidGeneralHouseworkForm, MaidCookingForm, MaidFoodHandlingPreferenceForm,
    MaidDietaryRestrictionForm, MaidEmploymentHistoryForm
)

from .models import (
    Maid, MaidBiodata, MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare,
    MaidDisabledCare, MaidGeneralHousework, MaidCooking, 
    MaidFoodHandlingPreference, MaidDietaryRestriction, MaidEmploymentHistory
)

# Start of Views

# Template Views

# Redirect Views
class MaidTogglePublished(LoginRequiredMixin, RedirectView):
    pattern_name = ''

    def get_redirect_url(self, *args, **kwargs):
        try:
            maid = Maid.objects.get(
                pk = kwargs.get('pk')
            )
        except Maid.DoesNotExist:
            messages.error(
                self.request,
                'This maid does not exist'
            )
        else:
            if maid.agency != Agency.objects.get(
                pk = self.request.user.pk
            ):
                messages.error(
                    self.request,
                    '''
                        You do not have the permission to modify the status 
                        of this maid
                    '''
                )

            maid.published = not maid.published
            maid.save()
            kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)
        
# List Views
class MaidList(ListFilteredMixin, ListView):
    context_object_name = 'maid'
    http_method_names = ['get']
    model = Maid
    queryset = Maid.objects.filter(published=True)
    template_name = 'maid-list.html'
    filter_set = MaidFilter

class MaidEmploymentHistoryList(LoginRequiredMixin, ListView):
    context_object_name = 'maid_employment_history_list'
    http_method_names = ['get']
    model = MaidEmploymentHistory
    template_name = 'maid-employment-history-list.html'

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
    template_name = 'maid-detail.html'

# Create Views
class MaidCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'maid'
    form_class = MaidCreationForm
    http_method_names = ['get','post']
    model = Maid
    template_name = 'maid-create.html'
    success_url = reverse_lazy('')

    def form_valid(self, form):
        form.instance.agency = self.request.user
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

class MaidFoodHandlingPreferenceCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'maid_food_handling_preference'
    form_class = MaidFoodHandlingPreferenceForm
    http_method_names = ['get','post']
    model = MaidFoodHandlingPreference
    template_name = 'maid-food-handling-preference-create.html'
    success_url = reverse_lazy('')

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.pk_url_kwarg
        )
        return super().form_valid(form)

class MaidDietaryRestrictionCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'maid_dietary_restriction'
    form_class = MaidDietaryRestrictionForm
    http_method_names = ['get','post']
    model = MaidDietaryRestriction
    template_name = 'maid-dietary-restriction-create.html'
    success_url = reverse_lazy('')

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.pk_url_kwarg
        )
        return super().form_valid(form)

class MaidEmploymentHistoryCreate(LoginRequiredMixin, CreateView):
    context_object_name = 'maid_employment_history'
    form_class = MaidEmploymentHistoryForm
    http_method_names = ['get','post']
    model = MaidEmploymentHistory
    template_name = 'maid-employment-history-create.html'
    success_url = reverse_lazy('')

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.pk_url_kwarg
        )
        return super().form_valid(form)

# Update Views
class MaidUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid'
    form_class = MaidCreationForm
    http_method_names = ['get','post']
    model = Maid
    template_name = 'maid-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Maid.objects.get(
            pk = self.kwargs.pk_url_kwarg,
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

class MaidBiodataUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_biodata'
    form_class = MaidBiodataForm
    http_method_names = ['get','post']
    model = MaidBiodata
    template_name = 'maid-biodata-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidBiodata.objects.get(
            maid = Maid.objects.get(
                pk = self.pk_url_kwarg
            )
        )

class MaidFamilyDetailsUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_family_details'
    form_class = MaidFamilyDetailsForm
    http_method_names = ['get','post']
    model = MaidFamilyDetails
    template_name = 'maid-family-details-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidFamilyDetails.objects.get(
            maid = Maid.objects.get(
                pk = self.pk_url_kwarg
            )
        )

class MaidInfantChildCareUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_infant_child_care'
    form_class = MaidInfantChildCareForm
    http_method_names = ['get','post']
    model = MaidInfantChildCare
    template_name = 'maid-infant-child-care-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidInfantChildCare.objects.get(
            maid = Maid.objects.get(
                pk = self.pk_url_kwarg
            )
        )

class MaidElderlyCareUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_elderly_care'
    form_class = MaidElderlyCareForm
    http_method_names = ['get','post']
    model = MaidElderlyCare
    template_name = 'maid-elderly-care-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidElderlyCare.objects.get(
            maid = Maid.objects.get(
                pk = self.pk_url_kwarg
            )
        )

class MaidDisabledCareUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_disabled_care'
    form_class = MaidDisabledCareForm
    http_method_names = ['get','post']
    model = MaidDisabledCare
    template_name = 'maid-disabled-care-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidDisabledCare.objects.get(
            maid = Maid.objects.get(
                pk = self.pk_url_kwarg
            )
        )

class MaidGeneralHouseworkUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_general_housework'
    form_class = MaidGeneralHouseworkForm
    http_method_names = ['get','post']
    model = MaidGeneralHousework
    template_name = 'maid-general-housework-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidGeneralHousework.objects.get(
            maid = Maid.objects.get(
                pk = self.pk_url_kwarg
            )
        )

class MaidCookingUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_cooking'
    form_class = MaidCookingForm
    http_method_names = ['get','post']
    model = MaidCooking
    template_name = 'maid-cooking-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidCooking.objects.get(
            maid = Maid.objects.get(
                pk = self.pk_url_kwarg
            )
        )

class MaidEmploymentHistoryUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'maid_employment_history'
    form_class = MaidEmploymentHistoryForm
    http_method_names = ['get','post']
    model = MaidEmploymentHistory
    template_name = 'maid-employment-history-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidEmploymentHistory.objects.get(
            pk = self.pk_url_kwarg,
            maid__agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

# Delete Views
class MaidDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'maid'
    http_method_names = ['get','post']
    model = Maid
    template_name = 'maid-delete.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Maid.objects.get(
            pk = self.kwargs.pk_url_kwarg,
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

class MaidFoodHandlingPreferenceDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'maid_food_handling_preference'
    http_method_names = ['get','post']
    model = MaidFoodHandlingPreference
    template_name = 'maid-food-handling-preference-delete.html'
    success_url = reverse_lazy('')

class MaidDietaryRestrictionDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'maid_dietary_restriction'
    http_method_names = ['get','post']
    model = MaidDietaryRestriction
    template_name = 'maid-dietary-restriction-delete.html'
    success_url = reverse_lazy('')

class MaidEmploymentHistoryDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'maid_employment_history'
    http_method_names = ['get','post']
    model = MaidEmploymentHistory
    template_name = 'maid-employment-history-delete.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return MaidEmploymentHistory.objects.get(
            pk = self.pk_url_kwarg,
            maid__agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )