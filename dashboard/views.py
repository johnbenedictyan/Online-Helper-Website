# Imports from django
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps
from agency.models import Agency
from maid.models import Maid

# Imports from local app

# Start of Views

# Template Views

# Redirect Views
class DashboardMaidTogglePublished(LoginRequiredMixin, RedirectView):
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
class DashboardMaidList(LoginRequiredMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    template_name = 'dashboard-maid-list.html'

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
