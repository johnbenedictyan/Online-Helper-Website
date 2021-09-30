from typing import Any, Optional

# Django Imports
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

# Project Apps Imports
from accounts.models import PotentialEmployer
from accounts.mixins import PotentialEmployerGrpRequiredMixin
from agency.mixins import OMStaffRequiredMixin
from onlinemaid.mixins import SuccessMessageMixin

# App Imports
from .forms import GeneralEnquiryForm
from .models import GeneralEnquiry, MaidShortlistedEnquiryIM, ShortlistedEnquiry

# Start of Views


class GeneralEnquiryView(SuccessMessageMixin, CreateView):
    context_object_name = 'general_enquiry'
    form_class = GeneralEnquiryForm
    http_method_names = ['get', 'post']
    model = GeneralEnquiry
    template_name = 'general_enquiry.html'
    success_url = reverse_lazy('home')
    success_message = 'General Enquiry created'

    def form_valid(self, form):
        if self.request.user:
            form.instance.potential_employer = PotentialEmployer.objects.get(
                user=self.request.user
            )
            form.instance.last_modified = self.request.user
        return super().form_valid(form)


class DeactivateGeneralEnquiryView(PotentialEmployerGrpRequiredMixin,
                                   RedirectView):
    http_method_names = ['get']
    pattern_name = None
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        try:
            selected_enquiry = GeneralEnquiry.objects.get(
                pk=kwargs.get(
                    self.pk_url_kwarg
                ),
                active=True
            )
        except GeneralEnquiry.DoesNotExist:
            messages.error(
                self.request,
                'This enquiry does not exist'
            )
        else:
            user_potential_employer = PotentialEmployer.objects.get(
                user=self.request.user
            )
            if selected_enquiry.potential_employer == user_potential_employer:
                selected_enquiry.active = False
                selected_enquiry.save()
            else:
                messages.error(
                    self.request,
                    'This enquiry does not exist'
                )
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)


class ToggleApproveEnquiryView(OMStaffRequiredMixin, RedirectView):
    http_method_names = ['get']
    pattern_name = 'admin_panel_enquiry_list'
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        try:
            selected_enquiry = GeneralEnquiry.objects.get(
                pk=kwargs.get(
                    self.pk_url_kwarg
                ),
                active=True
            )
        except GeneralEnquiry.DoesNotExist:
            messages.error(
                self.request,
                'This enquiry does not exist'
            )
        else:
            selected_enquiry.approved = not selected_enquiry.approved
            selected_enquiry.last_modified = self.request.user
            selected_enquiry.save()
        kwargs.pop('pk')
        return super().get_redirect_url(*args, **kwargs)


class EnquiryListView(PotentialEmployerGrpRequiredMixin, ListView):
    context_object_name = 'enquiries'
    http_method_names = ['get']
    model = GeneralEnquiry
    template_name = 'list/enquiry-list.html'

    def get_queryset(self):
        return GeneralEnquiry.objects.filter(
            potential_employer__user=self.request.user
        )


class SuccessfulEnquiryView(TemplateView):
    http_method_names = ['get']
    template_name = 'successful-enquiry.html'


class BaseApproveEnquiryView(RedirectView):
    object_class = None
    pk_url_kwarg = 'pk'

    def get_object(self):
        return get_object_or_404(
            self.object_class,
            pk=self.kwargs.get(
                self.pk_url_kwarg
            ),
            approved=False
        )

    def get_redirect_url(self, *args, **kwargs):
        enquiry = self.get_object()
        enquiry.approve(user=self.request.user)
        kwargs.pop(self.pk_url_kwarg)
        return reverse_lazy(
            'admin_panel'
        )


class ApproveGeneralEnquiryView(BaseApproveEnquiryView):
    object_class = GeneralEnquiry


class ApproveShortlistedlEnquiryView(BaseApproveEnquiryView):
    object_class = ShortlistedEnquiry


class RejectGeneralEnquiryView(BaseApproveEnquiryView):
    object_class = GeneralEnquiry

    def get_redirect_url(self, *args, **kwargs):
        enquiry = self.get_object()
        enquiry.reject()
        kwargs.pop(self.pk_url_kwarg)
        return reverse_lazy(
            'admin_panel'
        )


class RejectShortlistedEnquiryView(BaseApproveEnquiryView):
    object_class = ShortlistedEnquiry

    def get_redirect_url(self, *args, **kwargs):
        enquiry = self.get_object()
        enquiry.reject()
        kwargs.pop(self.pk_url_kwarg)
        return reverse_lazy(
            'admin_panel'
        )


class AcceptShortlistedEnquiry(RedirectView):
    http_method_names = ['get']
    pattern_name = 'fdw_account_detail'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        try:
            maid_shortlist_enquiry_im = MaidShortlistedEnquiryIM.objects.get(
                shortlisted_enquiry__pk=self.kwargs.get('pk'),
                maid__pk=self.kwargs.get('maid_pk')
            )
        except MaidShortlistedEnquiryIM.DoesNotExist:
            pass
        else:
            maid_shortlist_enquiry_im.set_status_accepted()
        finally:
            kwargs = {}
            return super().get_redirect_url(*args, **kwargs)


class RejectShortlistedEnquiry(RedirectView):
    http_method_names = ['get']
    pattern_name = 'fdw_account_detail'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        try:
            maid_shortlist_enquiry_im = MaidShortlistedEnquiryIM.objects.get(
                shortlisted_enquiry__pk=self.kwargs.get('pk'),
                maid__pk=self.kwargs.get('maid_pk')
            )
        except MaidShortlistedEnquiryIM.DoesNotExist:
            pass
        else:
            maid_shortlist_enquiry_im.set_status_rejected()
        finally:
            kwargs = {}
            return super().get_redirect_url(*args, **kwargs)
