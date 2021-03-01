# Imports from django
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Imports from foreign installed apps
from onlinemaid.mixins import SuccessMessageMixin

# Imports from local app
from .forms import EmployerCreationForm, SignInForm, AgencySignInForm
from .models import Employer
from .mixins import VerifiedEmployerMixin, PotentialEmployerRequiredMixin

# Start of Views

## Views that inherit from inbuilt django views
class SignInView(SuccessMessageMixin, LoginView):
    template_name = 'base/sign-in.html'
    authentication_form = SignInForm
    success_message = 'Successful Login'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        request = self.request
        if(
            request.META.get('QUERY_STRING') == 'next=' + reverse(
                'maid_list'
            )
        ):
            kwargs.update({
                'show_disclaimer': True
            })
        return kwargs

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        else:
            if not self.success_url:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a success_url."
                )
            return str(self.success_url)  # success_url may be lazy
    
class AgencySignInView(SuccessMessageMixin, LoginView):
    template_name = 'base/agency-sign-in.html'
    authentication_form = AgencySignInForm
    success_message = 'Successful Login'
    success_url = reverse_lazy('dashboard_home')
    
    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        else:
            if not self.success_url:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a success_url."
                )
            return str(self.success_url)  # success_url may be lazy
        
## Template Views

## Redirect Views
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

## Detail Views
class EmployerDetail(PotentialEmployerRequiredMixin, VerifiedEmployerMixin,
                     DetailView):
    context_object_name = 'employer'
    http_method_names = ['get']
    model = Employer
    template_name = 'detail/employer-detail.html'

## Create Views
class EmployerCreate(SuccessMessageMixin, CreateView):
    context_object_name = 'employer'
    form_class = EmployerCreationForm
    http_method_names = ['get','post']
    model = Employer
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

## Update Views
class EmployerUpdate(SuccessMessageMixin, PotentialEmployerRequiredMixin,
                     VerifiedEmployerMixin, UpdateView):
    context_object_name = 'employer'
    form_class = EmployerCreationForm
    http_method_names = ['get','post']
    model = Employer
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

## Delete Views
class EmployerDelete(SuccessMessageMixin, PotentialEmployerRequiredMixin,
                     VerifiedEmployerMixin, DeleteView):
    context_object_name = 'employer'
    http_method_names = ['post']
    model = Employer
    success_url = reverse_lazy('home')
    success_message = 'Account deleted'
