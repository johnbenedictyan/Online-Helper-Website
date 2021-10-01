from typing import Dict, Any, Optional

# Django Imports
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.db import models
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Foreign Apps Imports
from enquiry.constants import EnquiryStatusChoices
from enquiry.models import MaidShortlistedEnquiryIM
from maid.models import Maid
from onlinemaid.constants import AUTHORITY_GROUPS, AG_OWNERS, T
from onlinemaid.mixins import SuccessMessageMixin

# Imports from local app
from .forms import (
    EmployerCreationForm, SignInForm, AgencySignInForm,
    CustomPasswordResetForm, EmailUpdateForm, FDWAccountCreationForm
)
from .models import FDWAccount, PotentialEmployer
from .mixins import PotentialEmployerGrpRequiredMixin

# Start of Views


class BaseLoginView(SuccessMessageMixin, LoginView):
    success_message = 'Successful Login'

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        else:
            if not self.success_url:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a success_url."
                )
            return str(self.success_url)


class SignInView(BaseLoginView):
    template_name = 'base/sign-in.html'
    authentication_form = SignInForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        next_hop_maid_string = 'next=' + reverse('maid_list')
        if next_hop_maid_string in self.request.META.get('QUERY_STRING'):
            kwargs.update({
                'show_disclaimer': True
            })
        return kwargs


class AgencySignInView(BaseLoginView):
    template_name = 'base/agency-sign-in.html'
    authentication_form = AgencySignInForm
    success_url = reverse_lazy('dashboard_home')

    def get_success_url(self):
        for auth_name in AUTHORITY_GROUPS:
            if self.request.user.groups.filter(name=auth_name).exists():
                authority = auth_name
                if (
                    authority == AG_OWNERS and
                    self.request.user.agency_owner.is_test_email()
                ):
                    success_url = reverse_lazy('user_email_update')
                    return success_url
        return super().get_success_url()


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'form/password-reset-form.html'


class SignOutView(LoginRequiredMixin, RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        messages.success(
            self.request,
            'Log out successful',
            extra_tags='sucess'
        )
        return super().get_redirect_url(*args, **kwargs)


class PotentialEmployerDetail(PotentialEmployerGrpRequiredMixin, DetailView):
    context_object_name = 'employer'
    http_method_names = ['get']
    model = PotentialEmployer
    template_name = 'detail/employer-detail.html'
    potential_employer = None

    def get_object(self, queryset: Optional[models.query.QuerySet] = ...) -> T:
        self.potential_employer = PotentialEmployer.objects.get(
            user=self.request.user
        )
        return self.potential_employer

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'documents': self.potential_employer.get_documents(),
            'enquiries': self.potential_employer.get_enquiries()
        })
        return context


class PotentialEmployerCreate(SuccessMessageMixin, CreateView):
    context_object_name = 'employer'
    form_class = EmployerCreationForm
    http_method_names = ['get', 'post']
    model = PotentialEmployer
    template_name = 'create/employer-create.html'
    success_url = reverse_lazy('home')
    form_type = 'CREATE'
    success_message = 'Account created'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'form_type': self.form_type
        })
        return kwargs


class PotentialEmployerUpdate(SuccessMessageMixin,
                              PotentialEmployerGrpRequiredMixin, UpdateView):
    context_object_name = 'employer'
    form_class = EmployerCreationForm
    http_method_names = ['get', 'post']
    model = PotentialEmployer
    template_name = 'update/employer-update.html'
    success_url = reverse_lazy('employer_detail')
    form_type = 'UPDATE'
    success_message = 'Account details updated'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'form_type': self.form_type,
            'email_address': self.object.user.email
        })
        return kwargs


class PotentialEmployerDelete(SuccessMessageMixin,
                              PotentialEmployerGrpRequiredMixin, DeleteView):
    context_object_name = 'employer'
    http_method_names = ['post']
    model = PotentialEmployer
    success_url = reverse_lazy('home')
    success_message = 'Account deleted'


class FDWAccountCreate(SuccessMessageMixin, CreateView):
    context_object_name = 'fdw'
    form_class = FDWAccountCreationForm
    http_method_names = ['get', 'post']
    model = FDWAccount
    template_name = 'create/fdw-create.html'
    success_url = reverse_lazy('home')
    form_type = 'CREATE'
    success_message = 'Account created'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'form_type': self.form_type
        })
        return kwargs


class FDWAccountDetail(DetailView):
    context_object_name = 'fdw'
    http_method_names = ['get']
    model = FDWAccount
    template_name = 'detail/fdw-account-detail.html'

    def get_object(self, queryset=None):
        return FDWAccount.objects.get(
            user=self.request.user
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        maid_qs = Maid.objects.filter(
            fdw_account__user=self.request.user
        )
        context.update({
            'jobs': MaidShortlistedEnquiryIM.objects.filter(
                maid__in=maid_qs,
                status=EnquiryStatusChoices.OPEN
            )
        })
        return context


class UserEmailUpdate(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = EmailUpdateForm
    template_name = 'update/email-update.html'
    success_url = reverse_lazy('dashboard_home')

    def get_object(self):
        return get_user_model().objects.get(
            pk=self.request.user.pk
        )

    def form_valid(self, form):
        for auth_name in AUTHORITY_GROUPS:
            if self.request.user.groups.filter(name=auth_name).exists():
                authority = auth_name
                if authority == AG_OWNERS:
                    self.request.user.agency_owner.unset_test_email()

        return super().form_valid(form)

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs
