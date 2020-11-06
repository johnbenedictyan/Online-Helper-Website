# Imports from django
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.base import RedirectView, TemplateView

# Imports from foreign installed apps
from maid.models import Maid

# Imports from local apps

# Start of Views

## Redirect Views
class AddTo(RedirectView):
    pattern_name = 'maid_list'

    def get_redirect_url(self, *args, **kwargs):
        current_shortlist = self.request.session.get('shortlist',[])
        try:
            selected_maid = Maid.objects.get(
                pk = kwargs.get('pk')
            )
        except Maid.DoesNotExist:
            messages.error(
                self.request,
                'This maid does not exist'
            )
        else:
            if selected_maid.published == False:
                messages.error(
                self.request,
                    'This maid cannot be shortlisted at the moment'
                )
            else:
                self.request.session['shortlist'] = current_shortlist.push(
                    selected_maid.pk
                )
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

class RemoveFrom(RedirectView):
    pattern_name = 'maid_list'

    def get_redirect_url(self, *args, **kwargs):
        current_shortlist = self.request.session.get('shortlist',[])
        try:
            selected_maid = Maid.objects.get(
                pk = kwargs.get('pk')
            )
        except Maid.DoesNotExist:
            messages.error(
                self.request,
                'This maid does not exist'
            )
        else:
            if selected_maid.pk not in current_shortlist:
                messages.error(
                self.request,
                    'This maid is not in your shortlist'
                )
            else:
                self.request.session['shortlist'] = current_shortlist.remove(
                    selected_maid.pk
                )
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

## Template Views
class ViewShortlist(TemplateView):
    template_name = "shortlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shortlist'] = self.request.session.get('shortlist', [])
        return context
