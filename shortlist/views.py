# Imports from django
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import RedirectView, TemplateView

# Imports from foreign installed apps
from enquiry.forms import MaidEnquiryForm
from enquiry.models import MaidEnquiry
from maid.models import Maid

# Imports from local apps

# Start of Views

## Redirect Views
class AddTo(RedirectView):
    pattern_name = 'maid_list'

    def get_redirect_url(self, *args, **kwargs):
        current_shortlist = self.request.session.get('shortlist', [])
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
            elif selected_maid.pk in current_shortlist:
                messages.error(
                    self.request,
                    'This maid is already in your shortlist'
                )
            else:
                current_shortlist.append(
                    selected_maid.pk
                )
                self.request.session['shortlist'] = current_shortlist
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

class RemoveFrom(RedirectView):
    pattern_name = 'maid_list'

    def get_redirect_url(self, *args, **kwargs):
        current_shortlist = self.request.session.get('shortlist', [])
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
                current_shortlist.remove(
                    selected_maid.pk
                )
                self.request.session['shortlist'] = current_shortlist
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)

## Template Views
class ViewShortlist(CreateView):
    form_class = MaidEnquiryForm
    http_method_names = ['get', 'post']
    model = MaidEnquiry
    success_url = reverse_lazy('home')
    template_name = "shortlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.current_shortlist = self.request.session.get('shortlist', [])
        self.request.session['shortlist'] = self.current_shortlist
        context.update({
            'shortlist': Maid.objects.filter(
                pk__in=self.current_shortlist
            )
        })
        return context

    def form_valid(self, form):
        form.instance.employer = request.user
        res = super().form_valid(form)
        for maid_pk in self.current_shortlist:
            self.object.maids.add(Maid.objects.get(
                pk=maid_pk
            ))
        return res