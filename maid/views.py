# Global Imports
import json
from random import shuffle

# Django Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView

# 3rd party

# Imports from project-wide files
from onlinemaid.mixins import ListFilteredMixin, SuccessMessageMixin

# Foreign Apps Imports
from employer_documentation.mixins import PdfHtmlViewMixin

# Imports from local app
from .constants import MaidStatusChoices
from .filters import MaidFilter
from .forms import MaidLoanTransactionForm
from .mixins import (
    SpecificAgencyMaidLoginRequiredMixin, SpecificAgencyOwnerRequiredMixin
)
from .models import Maid, MaidLoanTransaction

# Start of Views

# Template Views

# Form Views

# Redirect Views


class BaseMaidRedirectView(RedirectView):
    pk_url_kwarg = 'pk'

    def get_object(self):
        return get_object_or_404(
            Maid,
            pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        )


class MaidTogglePublished(BaseMaidRedirectView):
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        maid = super().get_object()
        maid.toggle_published()
        kwargs.pop(self.pk_url_kwarg)
        return reverse_lazy(
            'dashboard_maid_list'
        )


class MaidToggleFeatured(BaseMaidRedirectView):
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        maid = super().get_object()
        err_msg = maid.toggle_featured()
        if err_msg:
            messages.warning(
                self.request,
                'You have reached the limit of featured biodata',
                extra_tags='error'
            )
        kwargs.pop(self.pk_url_kwarg)
        return reverse_lazy(
            'dashboard_maid_list'
        )

# List Views


class MaidList(LoginRequiredMixin, ListFilteredMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    queryset = Maid.objects.filter(status=MaidStatusChoices.PUBLISHED)
    template_name = 'list/maid-list.html'
    filter_set = MaidFilter
    paginate_by = settings.MAID_PAGINATE_BY

# Detail Views


class MaidDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'maid'
    http_method_names = ['get']
    model = Maid
    template_name = 'detail/maid-detail.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        country_of_origin = self.object.country_of_origin
        languages = self.object.languages.all()
        similar_maids = Maid.objects.filter(
            country_of_origin=country_of_origin,
            responsibilities=self.object.get_main_responsibility(),
            languages__in=languages
        ).exclude(
            pk=self.object.pk
        ).distinct()
        kwargs.update({
            'similar_maids': similar_maids
        })
        return kwargs

# Create Views

# Update Views


class MaidLoanTransactionUpdate(SpecificAgencyMaidLoginRequiredMixin,
                                SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_loan_transaction'
    form_class = MaidLoanTransactionForm
    http_method_names = ['get', 'post']
    model = MaidLoanTransaction
    template_name = 'update/maid-agency-fee-transaction-update.html'
    success_message = 'Maid agency fee transaction updated'

    def get_object(self):
        return MaidLoanTransaction.objects.get(
            pk=self.kwargs.get('loan_transaction_pk'),
            maid=self.kwargs.get('pk'),
            maid__agency=self.request.user.agency_owner.agency
        )

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get('pk')
            }
        )

# Delete Views


class MaidDelete(SpecificAgencyOwnerRequiredMixin, SuccessMessageMixin,
                 DeleteView):
    context_object_name = 'maid'
    http_method_names = ['post']
    model = Maid
    success_url = reverse_lazy('dashboard_maid_list')
    check_type = 'maid'
    success_message = 'Maid deleted'

    def get_object(self):
        return Maid.objects.get(
            pk=self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency=self.request.user.agency_owner.agency
        )

# Generic Views


class MaidProfileView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            selected_maid = Maid.objects.get(
                pk=self.kwargs.get('pk')
            )
        except Maid.DoesNotExist:
            data = {
                'error': 'Maid does not exist'
            }
            return JsonResponse(data, status=404)
        else:
            data = {
                'salary': selected_maid.expected_salary,
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


class FeaturedMaidListView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body.decode('utf-8'))
        nationality = request_data.get('nationality')
        featured_maids = Maid.objects.filter(
            status='FEAT'
        )
        if nationality != 'ANY':
            featured_maids = featured_maids.filter(
                country_of_origin=nationality
            )

        shuffle(list(featured_maids))
        featured_maids = [
            {
                'pk': maid.pk,
                'photo_url': maid.photo.url,
                'name': maid.name,
                'country_of_origin': maid.get_country_of_origin_display(),
                'age': maid.age,
                'marital_status': maid.get_marital_status_display(),
                'type': maid.get_maid_type_display()
            } for maid in featured_maids
        ]
        data = {
            'featured_maids': featured_maids,
            'count': len(featured_maids),
            'nationality': nationality
        }
        return JsonResponse(data, status=200)

# PDF Views


class PdfMaidBiodataView(LoginRequiredMixin, PdfHtmlViewMixin, DetailView):
    model = Maid
    template_name = 'detail/pdf-biodata-detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()

        if hasattr(request.user, 'agency_employee'):
            context['agency_employee'] = request.user.agency_employee

        context['employment_history'] = self.object.employment_history.all()
        return self.generate_pdf_response(request, context)
