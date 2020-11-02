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
from .forms import AdvertisementCreationForm

from .models import Advertisement, AdvertisementLocation

# Start of Views

## Template Views

## Redirect Views

## List Views
class AdvertisementList(ListView):
    context_object_name = 'advertisement'
    http_method_names = ['get']
    model = Advertisement
    template_name = 'advertisement-list.html'

    def get_queryset(self):
        return Advertisement.objects.filter(
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

## Detail Views
class AdvertisementDetail(DetailView):
    context_object_name = 'advertisement'
    http_method_names = ['get']
    model = Advertisement
    template_name = 'advertisement-detail.html'
    
## Create Views
class AdvertisementCreate(CreateView):
    context_object_name = 'advertisement_plan'
    form_class = AdvertisementCreationForm
    http_method_names = ['get','post']
    model = Advertisement
    template_name = 'advertisement-plan-create.html'
    success_url = reverse_lazy('')

## Update Views
### Do we want to let them update the advertisement ad type or location?
class AdvertisementUpdate(LoginRequiredMixin, UpdateView):
    context_object_name = 'advertisement'
    form_class = AdvertisementCreationForm
    http_method_names = ['get','post']
    model = Advertisement
    template_name = 'advertisement-update.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Advertisement.objects.get(
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

## Delete Views
class AdvertisementDelete(LoginRequiredMixin, DeleteView):
    context_object_name = 'advertisement'
    http_method_names = ['get','post']
    model = Advertisement
    template_name = 'advertisement-delete.html'
    success_url = reverse_lazy('')

    def get_object(self, queryset=None):
        return Advertisement.objects.get(
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )