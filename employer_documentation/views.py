# Python
import secrets

# Django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy, resolve
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.views.generic import RedirectView
from django.views.generic.list import ListView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404

# From our apps
from agency.mixins import AgencyLoginRequiredMixin, GetAuthorityMixin
from . import models, forms, constants
from .formset import EmployerHouseholdFormSet, EmployerHouseholdFormSetHelper
from .mixins import *
from onlinemaid import constants as om_constants
from maid import constants as maid_constants

# Detail Views
class EmployerDetailView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    DetailView,
):
    model = models.Employer
    pk_url_kwarg = 'level_0_pk'
    template_name = 'detail/dashboard-employer-detail.html'

class EmployerDocDetailView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    DetailView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'detail/dashboard-case-detail.html'

# Create Views
class EmployerCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.Employer
    form_class = forms.EmployerForm
    template_name = 'employer_documentation/crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        if self.authority==om_constants.AG_SALES:
            form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.applicant_type == constants.EmployerTypeOfApplicantChoices.SPONSOR:
            success_url = reverse_lazy('employer_sponsor_create_route', kwargs={
                'level_0_pk': self.object.pk
            })
        
        elif self.object.applicant_type == constants.EmployerTypeOfApplicantChoices.JOINT_APPLICANT:
            success_url = reverse_lazy('employer_jointapplicant_create_route', kwargs={
                'level_0_pk': self.object.pk
            })
        
        else:
            success_url = reverse_lazy('employer_incomedetails_create_route', kwargs={
                'level_0_pk': self.object.pk
            })

        return success_url

class EmployerSponsorCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(
                self.pk_url_kwarg
            ), 
            'type_of_applicant':models.Employer.objects.get(pk=self.kwargs.get(self.pk_url_kwarg)).applicant_type,
        })
        return context

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer = models.Employer.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_incomedetails_update_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })

class EmployerJointApplicantCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.EmployerJointApplicant
    form_class = forms.EmployerJointApplicantForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(
                self.pk_url_kwarg
            ), 
            'type_of_applicant':models.Employer.objects.get(pk=self.kwargs.get(self.pk_url_kwarg)).applicant_type
        })
        return context

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer = models.Employer.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_incomedetails_update_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })

class EmployerIncomeDetailsCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.EmployerIncome
    form_class = forms.EmployerIncomeDetailsForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.get_object().applicant_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        type_of_applicant = self.get_object().applicant_type
        monthly_income_label = constants.monthly_income_label.get(
            type_of_applicant
        )
        kwargs['monthly_income_label'] = monthly_income_label
        return kwargs

    def form_valid(self, form):
        form.instance.employer = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.employer.household_details_required:
            return reverse_lazy('employer_householddetails_update_route', kwargs={
                'level_0_pk': self.object.employer.pk,
            })
        else:
            return reverse_lazy('dashboard_employers_list')

class EmployerDocCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView,
):
    model = models.EmployerDoc
    form_class = forms.EmployerDocForm
    template_name = 'employer_documentation/crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        kwargs['agency_id'] = self.agency_id
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('servicefee_update_route', kwargs={
            'level_1_pk': self.object.pk
        })
        return success_url

class DocServiceFeeScheduleCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocServiceFeeSchedule
    form_class = forms.DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('serviceagreement_update_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url

class DocServAgmtEmpCtrCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocServAgmtEmpCtr
    form_class = forms.DocServAgmtEmpCtrForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        kwargs['level_1_pk'] = self.kwargs.get(
            self.pk_url_kwarg
        )
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.employer_doc.fdw.maid_type == maid_constants.TypeOfMaidChoices.NEW:
            success_url = reverse_lazy('safetyagreement_update_route', kwargs={
                'level_1_pk': self.object.employer_doc.pk
            })
        else:
            success_url = reverse_lazy('docupload_update_route', kwargs={
                'level_1_pk': self.object.employer_doc.pk
            })
        return success_url

class DocSafetyAgreementCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocSafetyAgreement
    form_class = forms.DocSafetyAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )

        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('docupload_update_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url

class DocUploadCreateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocUpload
    form_class = forms.DocUploadForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard_case_list')

# Update Views
class EmployerUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.Employer
    form_class = forms.EmployerForm
    template_name = 'employer_documentation/crispy_form.html'
    pk_url_kwarg = 'level_0_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(
                self.pk_url_kwarg
            ), 
            'type_of_applicant': models.Employer.objects.get(
                pk=self.kwargs.get(
                    self.pk_url_kwarg
                )
            ).applicant_type
        })

        try:
            sponsor_pk = models.Employer.objects.get(
                pk=self.kwargs.get(
                    self.pk_url_kwarg
                )
            ).rn_sponsor_employer.pk
        except ObjectDoesNotExist:
            pass
        else:
            context.update({
                'sponsor_pk': sponsor_pk
            })
        
        try:
           joint_application_pk = models.Employer.objects.get(
                pk=self.kwargs.get(
                    self.pk_url_kwarg
                )
            ).rn_ja_employer.pk
        except ObjectDoesNotExist:
            pass
        else:
            context.update({
                'joint_application_pk': joint_application_pk
            })

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def get_success_url(self):
        if self.object.applicant_type == constants.EmployerTypeOfApplicantChoices.SPONSOR:
            success_url = reverse_lazy('employer_sponsor_update_route', kwargs={
                'level_0_pk': self.object.pk
            })
        elif self.object.applicant_type == constants.EmployerTypeOfApplicantChoices.JOINT_APPLICANT:
            success_url = reverse_lazy('employer_jointapplicant_update_route', kwargs={
                'level_0_pk': self.object.pk
            })
        else:
            success_url = reverse_lazy('employer_incomedetails_update_route', kwargs={
                'level_0_pk': self.object.pk
            })
        return success_url

class EmployerSponsorUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_sponsor_employer

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('employer_sponsor_create_route', kwargs={
                    'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.object.employer.pk, 
            'type_of_applicant': self.object.employer.applicant_type,
            'sponsor_pk': self.object.pk
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('employer_incomedetails_update_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })
        return success_url

class EmployerDocJointApplicantUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerJointApplicant
    form_class = forms.EmployerJointApplicantForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_ja_employer

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('employer_jointapplicant_create_route', kwargs={
                    'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(
                self.pk_url_kwarg
            ), 
            'type_of_applicant': models.Employer.objects.get(
                pk=self.kwargs.get(
                    self.pk_url_kwarg
                )
            ).applicant_type,
            'joint_application_pk': self.object.pk
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('employer_incomedetails_update_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })
        return success_url

class EmployerIncomeDetailsUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerIncome
    form_class = forms.EmployerIncomeDetailsForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_income_employer

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('employer_incomedetails_create_route', kwargs={
                    'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(
                self.pk_url_kwarg
            ), 
            'type_of_applicant':models.Employer.objects.get(pk=self.kwargs.get(self.pk_url_kwarg)).applicant_type
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        type_of_applicant = self.object.employer.applicant_type
        monthly_income_label = constants.monthly_income_label.get(
            type_of_applicant
        )
        kwargs['monthly_income_label'] = monthly_income_label
        return kwargs

    def get_success_url(self):
        if self.object.employer.household_details_required:
            success_url = reverse_lazy('employer_householddetails_update_route', kwargs={
                'level_0_pk': self.object.employer.pk
            })
        else:
            success_url = reverse_lazy('dashboard_employers_list')
        return success_url

class EmployerDocUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerDoc
    form_class = forms.EmployerDocForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.object.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        kwargs['agency_id'] = self.agency_id
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('servicefee_update_route', kwargs={
            'level_1_pk': self.object.pk
        })
        return success_url

class DocServiceFeeScheduleUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocServiceFeeSchedule
    form_class = forms.DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_servicefeeschedule_ed

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('servicefee_create_route', kwargs={
                    'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        kwargs['level_1_pk'] = self.kwargs.get(
            self.pk_url_kwarg
        )
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('serviceagreement_update_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url

class DocServAgmtEmpCtrUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocServAgmtEmpCtr
    form_class = forms.DocServAgmtEmpCtrForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_serviceagreement_ed

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('serviceagreement_create_route', kwargs={
                    'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        kwargs['level_1_pk'] = self.kwargs.get(
            self.pk_url_kwarg
        )
        return kwargs

    def get_success_url(self):
        if self.object.employer_doc.fdw.maid_type == maid_constants.TypeOfMaidChoices.NEW:
            success_url = reverse_lazy('safetyagreement_update_route', kwargs={
                'level_1_pk': self.object.employer_doc.pk
            })
        else:
            success_url = reverse_lazy('docupload_update_route', kwargs={
                'level_1_pk': self.object.employer_doc.pk
            })
        return success_url

class DocSafetyAgreementUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocSafetyAgreement
    form_class = forms.DocSafetyAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_safetyagreement_ed

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('safetyagreement_create_route', kwargs={
                    'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        kwargs['level_1_pk'] = self.kwargs.get(
            self.pk_url_kwarg
        )
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('docupload_update_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url

class DocUploadUpdateView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocUpload
    form_class = forms.DocUploadForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_docupload_ed

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('docupload_create_route', kwargs={
                    'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def get_success_url(self):
        return reverse('dashboard_case_list')

# class CaseStatusUpdateView(
#     AgencyLoginRequiredMixin,
#     GetAuthorityMixin,
#     UpdateView
# ):
#     model = models.CaseStatus
#     form_class = forms.CaseStatusForm
#     pk_url_kwarg = 'level_1_pk'
#     template_name = 'employer_documentation/crispy_form.html'

#     def get_object(self):
#         return models.EmployerDoc.objects.get(
#             pk=self.kwargs.get(self.pk_url_kwarg)
#         ).rn_casestatus_ed

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['authority'] = self.authority
#         return kwargs

#     def get_success_url(self):
#         return reverse('case_detail_route', kwargs={
#             'level_1_pk': self.object.employer_doc.pk,
#         })

class CaseStatusUpdateView(GetAuthorityMixin, UpdateView):
    model = models.CaseStatus
    form_class = forms.CaseStatusForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return models.CaseStatus.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return HttpResponseRedirect(
                reverse('docupload_create_route', kwargs={
                    'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def get_success_url(self):
        referer_url = self.request.headers['Referer'].replace(
            self.request.headers['Origin'],
            ''
        )
        match = resolve(referer_url)
        if match.url_name == 'dashboard_status_list':
            return reverse_lazy('dashboard_status_list')
        else:
            return reverse_lazy('safetyagreement_update_route', kwargs={
                'level_1_pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            })

# class CaseSignatureSlugUpdateView(
#     AgencyLoginRequiredMixin,
#     GetAuthorityMixin,
#     UpdateView
# ):
#     model = models.CaseSignature
#     form_class = CaseSignatureSlugForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/crispy_form.html'
#     model_field_name = None # Aslog in urls.py
#     form_fields = None # Aslog in urls.py
#     success_url_route_name = None # Aslog in urls.py

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['model_field_name'] = self.model_field_name
#         kwargs['form_fields'] = self.form_fields
#         return kwargs

#     def get_success_url(self):
#         return reverse_lazy(self.success_url_route_name, kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#             'level_2_pk': self.object.pk,
#         })


# Delete Views
class EmployerDeleteView(
    CheckUserIsAgencyOwnerMixin,
    DeleteView
):
    model = models.Employer
    pk_url_kwarg = 'level_0_pk'
    success_url = reverse_lazy('dashboard_employers_list')

class EmployerDocDeleteView(
    CheckUserIsAgencyOwnerMixin,
    DeleteView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/employer_confirm_delete.html'
    success_url = reverse_lazy('dashboard_case_list')


# Signature Views
class SignatureUpdateByAgentView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.CaseSignature
    form_class = forms.SignatureForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/signature_form_agency.html'
    model_field_name = None
    form_fields = None

    def get_object(self):
        return models.CaseSignature.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['model_field_name'] = self.model_field_name
        kwargs['form_fields'] = self.form_fields
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_field_verbose_name'] = models.CaseSignature._meta.get_field(
            self.model_field_name).verbose_name
        return context

    def get_success_url(self):
        return reverse_lazy('case_detail_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk,
        })

# class VerifyUserTokenView(
#     SuccessMessageMixin,
#     UpdateView
# ):
#     model = models.CaseSignature
#     form_class = VerifyUserTokenForm
#     template_name = 'employer_documentation/token_form.html'
#     token_field_name = None # Assign this value in urls.py
#     success_url_route_name = None # Assign this value in urls.py
#     success_message = None # Assign this value in urls.py

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['slug'] = self.kwargs.get(self.slug_url_kwarg)
#         kwargs['session'] = self.request.session
#         kwargs['token_field_name'] = self.token_field_name
#         return kwargs

#     def get_success_url(self):
#         if self.success_url_route_name:
#             if self.token_field_name=='employer_token':
#                 slug = self.object.sigslug_employer_1
#             elif self.token_field_name=='fdw_token':
#                 slug = self.object.fdw_slug
#         else:
#             return reverse_lazy('home')
#         return reverse_lazy(self.success_url_route_name, kwargs={'slug':slug})

#     def get_success_message(self, cleaned_data):
#         return self.success_message % dict(cleaned_data,)

# class SignatureUpdateByTokenView(
#     SuccessMessageMixin,
#     CheckSignatureSessionTokenMixin,
#     UpdateView
# ):
#     model = models.CaseSignature
#     form_class = SignatureForm
#     template_name = 'employer_documentation/signature_form_token.html'
#     model_field_name = None # Assign this value in urls.py
#     token_field_name = None # Assign this value in urls.py
#     form_fields = None # Assign this value in urls.py
#     success_url_route_name = None # Assign this value in urls.py
#     success_message = None # Assign this value in urls.py

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['model_field_name'] = self.model_field_name
#         kwargs['form_fields'] = self.form_fields
#         return kwargs

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['model_field_verbose_name'] = CaseSignature._meta.get_field(
#             self.model_field_name).verbose_name
#         return context

#     def get_success_url(self):
#         if self.success_url_route_name:
#             if self.token_field_name=='employer_token':
#                 slug = self.object.sigslug_employer_1
#             elif self.token_field_name=='fdw_token':
#                 slug = self.object.fdw_slug
#         else:
#             return reverse_lazy('home')
        
#         if (
#             self.success_url_route_name=='token_signature_employer_spouse_route'
#             and not self.object.employer_doc.spouse_required
#         ):
#             return reverse_lazy('home')
#         else:
#             return reverse_lazy(
#                 self.success_url_route_name,
#                 kwargs={'slug':slug}
#             )

#     def get_success_message(self, cleaned_data):
#         return self.success_message % dict(cleaned_data,)


# PDF Views
class HtmlToRenderPdfAgencyView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()

        if self.use_repayment_table:
            context['repayment_table'] = self.calc_repayment_schedule()
        
        context['url_name'] = request.resolver_match.url_name
        return self.generate_pdf_response(request, context)

class UploadedPdfAgencyView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    DetailView
):
    # model = None # To be passed as parameter in urls.py
    # pk_url_kwarg = None # To be passed as parameter in urls.py
    # slug_url_kwarg = None # To be passed as parameter in urls.py
    as_attachment=False
    filename='document.pdf'
    field_name = None

    def get_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        ).rn_docupload_ed

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return FileResponse(
                getattr(self.object, self.field_name).open(),
                as_attachment=self.as_attachment,
                filename=self.filename,
                content_type='application/pdf'
            )
        except Exception:
            return HttpResponseRedirect(
                reverse('docupload_update_route', kwargs={
                    'level_1_pk': self.object.employer_doc.pk,
            }))

# class PdfGenericTokenView(
#     CheckSignatureSessionTokenMixin,
#     PdfHtmlViewMixin,
#     DetailView
# ):
#     model = models.CaseSignature
#     slug_url_kwarg = 'slug'
#     token_field_name = None

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data()

#         if self.use_repayment_table:
#             context['repayment_table'] = self.calc_repayment_schedule()

#         return self.generate_pdf_response(request, context)

# class PdfFileTokenView(
#     CheckSignatureSessionTokenMixin,
#     DetailView
# ):
#     model = models.CaseSignature
#     slug_url_kwarg = 'slug'
#     token_field_name = None
#     as_attachment=False
#     filename='document.pdf'

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object().employer_doc.rn_joborder_ed
#         try:
#             return FileResponse(
#                 open(self.object.job_order_pdf.path, 'rb'),
#                 as_attachment=self.as_attachment,
#                 filename=self.filename,
#                 content_type='application/pdf'
#             )
#         except Exception:
#             return HttpResponseRedirect(reverse('home'))

# class PdfArchiveSaveView(
#     AgencyLoginRequiredMixin,
#     GetAuthorityMixin,
#     PdfHtmlViewMixin,
#     DetailView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_1_pk'

#     def check_signatures(self, employer_doc):
#         if (
#             not employer_doc.rn_signatures_ed.employer_signature or
#             not employer_doc.rn_signatures_ed.fdw_signature or
#             not employer_doc.rn_signatures_ed.agency_staff_signature or
#             not employer_doc.rn_signatures_ed.employer_witness_signature or
#             not employer_doc.rn_signatures_ed.employer_witness_name or
#             not employer_doc.rn_signatures_ed.employer_witness_nric or
#             not employer_doc.rn_signatures_ed.fdw_witness_signature or
#             not employer_doc.rn_signatures_ed.fdw_witness_name or
#             not employer_doc.rn_signatures_ed.fdw_witness_nric or
#             not employer_doc.rn_signatures_ed.agency_staff_witness_signature or
#             not employer_doc.rn_signatures_ed.agency_staff_witness_name or
#             not employer_doc.rn_signatures_ed.agency_staff_witness_nric
#         ):
#             return 'Missing required signatures or witness details.'
        
#         if (
#             employer_doc.spouse_required and (
#                 not employer_doc.rn_signatures_ed.spouse_signature or
#                 not employer_doc.rn_signatures_ed.spouse_name or
#                 not employer_doc.rn_signatures_ed.spouse_nric
#             )
#         ):
#             return 'Missing spouse signature and/or details.'

#         if (
#             employer_doc.sponsor_required and (
#                 not employer_doc.rn_signatures_ed.sponsor_signature or
#                 not employer_doc.rn_signatures_ed.sponsor_name or
#                 not employer_doc.rn_signatures_ed.sponsor_nric
#             )
#         ):
#             return 'Missing sponsor signature and/or details.'
        
#         return False


#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data()
#         context['repayment_table'] = self.calc_repayment_schedule()

#         signatures_check = self.check_signatures(self.object)
#         if signatures_check:
#             messages.add_message(
#                 request,
#                 messages.WARNING,
#                 'Could not save documents. ' + signatures_check
#             )
#             return HttpResponseRedirect(reverse_lazy('dashboard_sales_list'))

#         instance = PdfArchive.objects.get(employer_doc=self.object)
#         folder = 'employer_documentation/pdf/'
#         templates = {
#             'f01_service_fee_schedule':     folder + '01-service-fee-schedule.html',
#             'f03_service_agreement':        folder + '03-service-agreement.html',
#             'f04_employment_contract':      folder + '04-employment-contract.html',
#             'f05_repayment_schedule':       folder + '05-repayment-schedule.html',
#             'f06_rest_day_agreement':       folder + '06-rest-day-agreement.html',
#             'f08_handover_checklist':       folder + '08-handover-checklist.html',
#             'f09_transfer_consent':         folder + '09-transfer-consent.html',
#             'f10_work_pass_authorisation':  folder + '10-work-pass-authorisation.html',
#             # 'f11_security_bond':            folder + '11-security-bond.html',
#             # 'f12_fdw_work_permit':          folder + '12-fdw-work-permit.html',
#             'f13_income_tax_declaration':   folder + '13-income-tax-declaration.html',
#             'f14_safety_agreement':         folder + '14-safety-agreement.html',
#         }
#         for field_name, template_name in templates.items():
#             # filename = template_name.split('/')[-1].split('.')[-2] + '.pdf'
#             filename = field_name + '.pdf'
#             relative_path = f'{self.object.pk}:{filename}'
#             pdf_file = self.generate_pdf_file(request, context, template_name)
#             file_wrapper = SimpleUploadedFile(
#                 relative_path,
#                 pdf_file,
#                 'application/pdf'
#             )
#             setattr(instance, field_name, file_wrapper)
#         instance.save()

#         return HttpResponseRedirect(reverse_lazy('dashboard_sales_list'))

# class PdfArchiveDetailView(
#     AgencyLoginRequiredMixin,
#     GetAuthorityMixin,
#     DetailView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_1_pk'
#     template_name = 'employer_documentation/pdfarchive_detail.html'

# Form Views
class EmployerHouseholdDetailsFormView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    SuccessMessageMixin,
    FormView
):
    form_class = EmployerHouseholdFormSet
    http_method_names = ['get', 'post']
    template_name = 'employer_documentation/crispy_form.html'
    pk_url_kwarg = 'level_0_pk'
    authority = ''
    agency_id = ''
    employer_id = ''
    success_message = 'Maid employment history updated'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'employer_id': self.employer_id,
            'level_0_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'type_of_applicant':models.Employer.objects.get(
                pk=self.kwargs.get(
                    self.pk_url_kwarg
                )
            ).applicant_type
        })
        income_obj = models.Employer.objects.get(
            pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        ).has_income_obj()
        if income_obj:
            context.update({
                'income_obj': income_obj
            })
        helper = EmployerHouseholdFormSetHelper()
        helper.form_tag = False
        context.update({
            'helper': helper
        })
        return context
    
    def get_formset_form_kwargs(self):
        self.employer_id = self.kwargs.get(
            self.pk_url_kwarg
        )
        kwargs = {
            'employer_id': self.employer_id
        }
        return kwargs
    
    def get_instance_object(self):
        return models.Employer.objects.get(
            pk=self.employer_id
        )
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.get_instance_object()
        })
        return kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(
            form_kwargs=self.get_formset_form_kwargs(),
            **self.get_form_kwargs()
        )
        
    def form_valid(self, form):
        form.save()
        if form.data.get('submitFlag') == 'True':
            return super().form_valid(form)
        else:
            return HttpResponseRedirect(
                reverse_lazy(
                    'employer_householddetails_update_route',
                    kwargs={
                        'level_0_pk':self.employer_id
                    }
                )
            )

    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_employers_list'
        )

class TokenVerificationFormView(FormView):
    form_class=forms.TokenVerificationForm
    http_method_names = ['get', 'post']

# Redirect Views
class GenerateSigSlugEmployer1View(AgencyLoginRequiredMixin, GetAuthorityMixin, RedirectView):
    model = models.CaseSignature
    pk_url_kwarg = 'level_1_pk'
    pattern_name = 'case_detail_route'

    def get_object(self):
        return self.model.objects.get_or_create(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg),
            defaults={'employer_doc': models.EmployerDoc.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))},
        )[0]

    def get_redirect_url(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.generate_sigslug_employer_1()
        kwargs={'level_1_pk': self.object.employer_doc.pk}
        return super().get_redirect_url(*args, **kwargs) + "#signatureUrlSection"

class RevokeSigSlugEmployer1View(AgencyLoginRequiredMixin, GetAuthorityMixin, RedirectView):
    model = models.CaseSignature
    pk_url_kwarg = 'level_1_pk'
    pattern_name = 'case_detail_route'

    def get_object(self):
        return self.model.objects.get_or_create(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg),
            defaults={'employer_doc': models.EmployerDoc.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))},
        )[0]

    def get_redirect_url(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.revoke_sigslug_employer_1()
        kwargs={'level_1_pk': self.object.employer_doc.pk}
        return super().get_redirect_url(*args, **kwargs) + "#signatureUrlSection"

class TokenChallengeEmployer1View(
    SuccessMessageMixin,
    FormView,
):
    model = models.CaseSignature
    form_class = forms.TokenChallengeEmployer1Form
    slug_url_kwarg = 'slug'
    template_name = 'employer_documentation/signature_challenge_form.html'

    def get_object(self):
        return get_object_or_404(
            self.model,
            sigslug_employer_1=self.kwargs.get(self.slug_url_kwarg)
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse(
            'challenge_employer1_route',
            kwargs={'slug': self.kwargs.get(self.slug_url_kwarg)}
        )

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs.update({
            'object':self.get_object()
        })
        return kwargs

class ArchiveCase(RedirectView):
    http_method_names = ['get']
    pattern_name = 'dashboard_case_list'

    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url(*args, **kwargs)

class CaseStatusAPIView(View):
    def get(self, request, *args, **kwargs):
        data = {}
        try:
            case_status = models.CaseStatus.objects.get(
                employer_doc__pk=request.GET.get('casePK')
            )
        except ObjectDoesNotExist:
            return JsonResponse(data, status=404)
        else:
            data = {
                'fdwNameInput': case_status.employer_doc.fdw.name,
                'ipaApprovalDateInput': case_status.ipa_approval_date,
                'fdwArrivalDateInput': case_status.arrival_date,
                'fdwShnEndDateInput': case_status.shn_end_date,
                'fdwThumbprintDateInput': case_status.thumb_print_date,
                'fdwWorkCommencementDateInput': case_status.fdw_work_commencement_date
            }
        return JsonResponse(data, status=200)
