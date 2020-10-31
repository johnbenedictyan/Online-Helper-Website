# Imports from django
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps
from agency.models import Agency

# Imports from local app
from .forms import (
    MaidCreationForm, MaidBiodataForm, MaidFamilyDetailsForm, 
    MaidInfantChildCareForm, MaidElderlyCareForm, MaidDisabledCareForm,
    MaidGeneralHouseworkForm, MaidCookingForm, MaidFoodHandlingPreferenceForm,
    MaidDietaryRestrictionForm
)

from .models import (
    Maid, MaidBiodata, MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare,
    MaidDisabledCare, MaidGeneralHousework, MaidCooking, 
    MaidFoodHandlingPreference, MaidDietaryRestriction
)

# Start of Views

# Template Views

# Redirect Views

# Detail Views
    
# Create Views
class MaidCreate(CreateView):
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

class MaidFoodHandlingPreferenceCreate(CreateView):
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

class MaidDietaryRestrictionCreate(CreateView):
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