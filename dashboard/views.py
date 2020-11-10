# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps
from agency.models import Agency
from maid.models import Maid

# Imports from local app

# Start of Views

# Template Views
class DashboardHomePage(LoginRequiredMixin, TemplateView):
    template_name = 'base/dashboard-home-page.html'

# Redirect Views

# List Views
class DashboardAccountList(LoginRequiredMixin, ListView):
    context_object_name = 'accounts'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/dashboard-account-list.html'

class DashboardMaidList(LoginRequiredMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/dashboard-maid-list.html'

    def get_queryset(self):
        return Maid.objects.get(
            agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

# Detail Views

# Create Views

# Update Views

# Delete Views
