# Imports from django
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps

# Imports from local app
from .forms import EmployerCreationForm, SignInForm
from .models import Employer
from .mixins import VerifiedEmployerMixin

# Start of Views

## Views that inherit from inbuilt django views
class SignInView(LoginView):
    template_name = 'base/sign-in.html'
    authentication_form = SignInForm

    def get_success_url(self):
        URL_DICT = {
            'A': reverse_lazy(
                'agency_detail',
                kwargs={
                    'pk':self.request.user.pk
                }),
            'AE': reverse_lazy(
                'agency_detail',
                kwargs={
                    'pk':self.request.user.agency.pk
                }),
            'E': reverse_lazy(
                'employer_detail',
                kwargs={
                    'pk':self.request.user.pk
                })
        }
        if self.request.user.role in URL_DICT:
            return URL_DICT[self.request.user.role]

        return super().get_success_url()

## Template Views

## Redirect Views
class SignOutView(LoginRequiredMixin, RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        messages.success(
            self.request,
            'Log out successful'
        )
        return super().get_redirect_url(*args, **kwargs)

## Detail Views
class EmployerDetail(LoginRequiredMixin, VerifiedEmployerMixin, DetailView):
    context_object_name = 'employer'
    http_method_names = ['get']
    model = Employer
    template_name = 'detail/employer-detail.html'

## Create Views
class EmployerCreate(CreateView):
    context_object_name = 'employer'
    form_class = EmployerCreationForm
    http_method_names = ['get','post']
    model = Employer
    template_name = 'create/employer-create.html'
    success_url = reverse_lazy('home')

## Update Views
class EmployerUpdate(LoginRequiredMixin, VerifiedEmployerMixin, UpdateView):
    context_object_name = 'employer'
    form_class = EmployerCreationForm
    http_method_names = ['get','post']
    model = Employer
    template_name = 'update/employer-update.html'
    success_url = reverse_lazy('')

## Delete Views
class EmployerDelete(LoginRequiredMixin, VerifiedEmployerMixin, DeleteView):
    context_object_name = 'employer'
    http_method_names = ['post']
    model = Employer
    success_url = reverse_lazy('home')
