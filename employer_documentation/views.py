# Django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy, resolve
from django.http import FileResponse, HttpResponseRedirect, JsonResponse, Http404
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
from . import models, forms, constants
from .formset import (
    EmployerHouseholdFormSet, EmployerHouseholdFormSetHelper, 
    MaidInventoryFormSet, MaidInventoryFormSetHelper
)

from .mixins import PdfHtmlViewMixin, CheckUserIsAgencyOwnerMixin
from onlinemaid import constants as om_constants
from maid import constants as maid_constants
from agency.mixins import AgencyAccessToEmployerDocAppMixin, GetAuthorityMixin

# Detail Views
class EmployerDetailView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DetailView,
):
    model = models.Employer
    pk_url_kwarg = 'level_0_pk'
    template_name = 'detail/dashboard-employer-detail.html'

class EmployerDocDetailView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DetailView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'detail/dashboard-case-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'employer_1_sigurl': self.object.rn_signatures_ed.get_sigurl('employer_1'),
            'employer_spouse_sigurl': self.object.rn_signatures_ed.get_sigurl('employer_spouse'),
            'sponsor_1_sigurl': self.object.rn_signatures_ed.get_sigurl('sponsor_1'),
            'sponsor_2_sigurl': self.object.rn_signatures_ed.get_sigurl('sponsor_2'),
            'joint_applicant_sigurl': self.object.rn_signatures_ed.get_sigurl('joint_applicant')
        })
        return context

# Create Views
class EmployerCreateView(
    AgencyAccessToEmployerDocAppMixin,
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

    # def form_valid(self, form):
    #     if self.authority==om_constants.AG_SALES:
    #         form.instance.agency_employee = self.request.user.agency_employee
    #     return super().form_valid(form)

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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, 'rn_sponsor_employer'):
            return HttpResponseRedirect(
                reverse('employer_sponsor_update_route', kwargs={
                    self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer = self.object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_incomedetails_update_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })

class EmployerJointApplicantCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.EmployerJointApplicant
    form_class = forms.EmployerJointApplicantForm
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, 'rn_ja_employer'):
            return HttpResponseRedirect(
                reverse('employer_jointapplicant_update_route', kwargs={
                    self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer = self.object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_incomedetails_update_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })

class EmployerIncomeDetailsCreateView(
    AgencyAccessToEmployerDocAppMixin,
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, 'rn_income_employer'):
            return HttpResponseRedirect(
                reverse('employer_incomedetails_update_route', kwargs={
                    self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        type_of_applicant = self.object.applicant_type
        monthly_income_label = constants.monthly_income_label.get(
            type_of_applicant
        )
        kwargs['monthly_income_label'] = monthly_income_label
        return kwargs

    def form_valid(self, form):
        form.instance.employer = self.object
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.employer.household_details_required:
            return reverse_lazy('employer_householddetails_update_route', kwargs={
                'level_0_pk': self.object.employer.pk,
            })
        else:
            return reverse_lazy('dashboard_employers_list')

class EmployerDocCreateView(
    AgencyAccessToEmployerDocAppMixin,
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocServiceFeeSchedule
    form_class = forms.DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, 'rn_servicefeeschedule_ed'):
            return HttpResponseRedirect(
                reverse('servicefee_update_route', kwargs={
                    self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.object
        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('serviceagreement_update_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url

class DocServAgmtEmpCtrCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocServAgmtEmpCtr
    form_class = forms.DocServAgmtEmpCtrForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, 'rn_serviceagreement_ed'):
            return HttpResponseRedirect(
                reverse('serviceagreement_update_route', kwargs={
                    self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        kwargs['level_1_pk'] = self.kwargs.get(
            self.pk_url_kwarg
        )
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.object
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocSafetyAgreement
    form_class = forms.DocSafetyAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, 'rn_safetyagreement_ed'):
            return HttpResponseRedirect(
                reverse('safetyagreement_update_route', kwargs={
                    self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.object

        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('docupload_update_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url

class DocUploadCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.DocUpload
    form_class = forms.DocUploadForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk = self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, 'rn_docupload_ed'):
            return HttpResponseRedirect(
                reverse('docupload_update_route', kwargs={
                    self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg),
            }))
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard_case_list')

# Update Views
class EmployerUpdateView(
    AgencyAccessToEmployerDocAppMixin,
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
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg), 
            'type_of_applicant': self.object.applicant_type,
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.object.employer.pk, 
            'type_of_applicant': self.object.employer.applicant_type,
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerJointApplicant
    form_class = forms.EmployerJointApplicantForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.object.employer.applicant_type,
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerIncome
    form_class = forms.EmployerIncomeDetailsForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.object.employer.applicant_type,
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
    AgencyAccessToEmployerDocAppMixin,
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
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocServiceFeeSchedule
    form_class = forms.DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocServAgmtEmpCtr
    form_class = forms.DocServAgmtEmpCtrForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocSafetyAgreement
    form_class = forms.DocSafetyAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.DocUpload
    form_class = forms.DocUploadForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
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

class CaseStatusUpdateView(GetAuthorityMixin, UpdateView):
    model = models.CaseStatus
    form_class = forms.CaseStatusForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_documentation/crispy_form.html'

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
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
    AgencyAccessToEmployerDocAppMixin,
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
        return self.model.objects.get(
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


# PDF Views
class HtmlToRenderPdfAgencyView(
    AgencyAccessToEmployerDocAppMixin,
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
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DetailView
):
    model = None # To be passed as parameter in urls.py
    pk_url_kwarg = None # To be passed as parameter in urls.py
    as_attachment=False
    filename='document.pdf'
    field_name = None

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

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

class HtmlToRenderPdfTokenView(
    PdfHtmlViewMixin,
    DetailView
):
    model = models.CaseSignature
    slug_url_kwarg = 'slug'
    stakeholder = None

    def get_object(self):
        slug = self.kwargs.get(self.slug_url_kwarg)
        stakeholder = self.model.reverse_sigslug_header_dict.get(slug[0:5])
        if stakeholder:
            self.stakeholder = stakeholder
            try:
                if stakeholder == 'employer_1':
                    obj = self.model.objects.get(
                        sigslug_employer_1=slug
                    ).employer_doc
                elif stakeholder == 'employer_spouse':
                    obj = self.model.objects.get(
                        sigslug_employer_spouse=slug
                    ).employer_doc
                elif stakeholder == 'sponsor_1':
                    obj = self.model.objects.get(
                        sigslug_sponsor_1=slug
                    ).employer_doc
                elif stakeholder == 'sponsor_2':
                    obj = self.model.objects.get(
                        sigslug_sponsor_2=slug
                    ).employer_doc
                elif stakeholder == 'joint_applicant':
                    obj = self.model.objects.get(
                        sigslug_joint_applicant=slug
                    ).employer_doc
                else:
                    obj = None
            except self.model.DoesNotExist:
                return None
            else:
                return obj
        else:
            # SLUG DOES NOT HAVE FRONT HEADER
            # TODO: Special Error Page thing
            pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        stakeholder_referrer_dict = {
            # Stakeholder: Referrer Url Name
            'employer_1':       'token_employer_signature_form_view',
            'employer_spouse':  'token_employer_spouse_signature_form_view',
            'sponsor_1':        'token_sponsor_1_signature_form_view',
            'sponsor_2':        'token_sponsor_2_signature_form_view',
            'joint_applicant':  'token_joint_applicant_signature_form_view'
        }
        url_route_name =  stakeholder_referrer_dict.get(self.stakeholder)
        referrer = '/' + '/'.join(request.META.get('HTTP_REFERER', '').split('/')[3:])
        rev_url = reverse(url_route_name, kwargs={
            'slug': self.kwargs.get(self.slug_url_kwarg)
        })
        if self.object and referrer == rev_url:
            context = self.get_context_data()
            if self.use_repayment_table:
                context['repayment_table'] = self.calc_repayment_schedule()
            return self.generate_pdf_response(request, context)
        else:
            return HttpResponseRedirect(reverse('error_404'))

# Form Views
class EmployerHouseholdDetailsFormView(
    AgencyAccessToEmployerDocAppMixin,
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
    
    def get_object(self):
        return models.Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

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

class MaidInventoryFormView(AgencyAccessToEmployerDocAppMixin, GetAuthorityMixin,  SuccessMessageMixin,
                            FormView):
    form_class = MaidInventoryFormSet
    http_method_names = ['get', 'post']
    template_name = 'employer_documentation/crispy_form.html'
    pk_url_kwarg = 'level_1_pk'
    authority = ''
    agency_id = ''
    employer_id = ''
    success_message = 'Maid inventory updated'
    
    def get_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(
                self.pk_url_kwarg
            )
        })
        helper = MaidInventoryFormSetHelper()
        helper.form_tag = False
        context.update({
            'helper': helper
        })
        return context
    
    def get_formset_form_kwargs(self):
        self.employer_doc_id = self.kwargs.get(
            self.pk_url_kwarg
        )
        kwargs = {
            'employer_doc_id': self.employer_doc_id
        }
        return kwargs
    
    def get_instance_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.employer_doc_id
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
                    'maid_inventory_update_route',
                    kwargs={
                        'level_1_pk':self.employer_doc_id
                    }
                )
            )
    
    def get_success_url(self) -> str:
        return reverse_lazy(
            'docupload_create_route',
            kwargs={
                'level_1_pk':self.employer_doc_id
            }
        )

class SignatureFormView(FormView):
    form_class = None
    slug_url_kwarg = 'slug'
    http_method_names = ['get', 'post']
    template_name = 'employer_documentation/signature_form_token.html'

    def get_object(self, request):
        url_name = resolve(request.path).url_name
        if url_name == 'token_employer_signature_form_view':
            return get_object_or_404(
                models.CaseSignature,
                sigslug_employer_1=self.kwargs.get(self.slug_url_kwarg)
            )
        elif url_name == 'token_employer_with_spouse_signature_form_view':
            return get_object_or_404(
                models.CaseSignature,
                sigslug_employer_1=self.kwargs.get(self.slug_url_kwarg)
            )
        elif url_name == 'token_employer_spouse_signature_form_view':
            return get_object_or_404(
                models.CaseSignature,
                sigslug_employer_spouse=self.kwargs.get(self.slug_url_kwarg)
            )
        elif url_name == 'token_sponsor_1_signature_form_view':
            return get_object_or_404(
                models.CaseSignature,
                sigslug_sponsor_1=self.kwargs.get(self.slug_url_kwarg)
            )
        elif url_name == 'token_sponsor_2_signature_form_view':
            return get_object_or_404(
                models.CaseSignature,
                sigslug_sponsor_2=self.kwargs.get(self.slug_url_kwarg)
            )
        elif url_name == 'token_joint_applicant_signature_form_view':
            return get_object_or_404(
                models.CaseSignature,
                sigslug_joint_applicant=self.kwargs.get(self.slug_url_kwarg)
            )
        else:
            return HttpResponseRedirect(reverse('error_404'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'slug': self.kwargs.get(self.slug_url_kwarg),
            'object': self.object,
        })
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object(request)
        referrer = '/' + '/'.join(request.META.get('HTTP_REFERER', '').split('/')[3:])
        rev_url = reverse(
            'token_challenge_route', 
            kwargs={
                'slug': self.kwargs.get(
                    self.slug_url_kwarg
                )
            }
        )
        if referrer == rev_url:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('error_404'))

    def get_success_url(self):
        return reverse('home')

class EmployerSignatureFormView(SignatureFormView):
    form_class = forms.EmployerSignatureForm

    def form_valid(self, form):
        self.object = super().get_object()
        self.object.employer_signature_1 = form.cleaned_data.get('employer_signature')
        self.object.save()
        return super().form_valid(form)

class EmployerWithSpouseSignatureFormView(SignatureFormView):
    form_class = forms.EmployerWithSpouseSignatureForm

    def form_valid(self, form):
        self.object = super().get_object()
        self.object.employer_signature_1 = form.cleaned_data.get('employer_signature')
        self.object.employer_spouse_signature = form.cleaned_data.get('employer_spouse_signature')
        self.object.save()
        return super().form_valid(form)

class Sponsor1SignatureFormView(SignatureFormView):
    form_class = forms.SponsorSignatureForm

    def form_valid(self, form):
        self.object = super().get_object()
        self.object.sponsor_1_signature = form.cleaned_data.get('sponsor_signature')
        self.object.save()
        return super().form_valid(form)

class Sponsor2SignatureFormView(SignatureFormView):
    form_class = forms.SponsorSignatureForm

    def form_valid(self, form):
        self.object = super().get_object()
        self.object.sponsor_2_signature = form.cleaned_data.get('sponsor_signature')
        self.object.save()
        return super().form_valid(form)

class EmployerWithJointApplicantSignatureFormView(SignatureFormView):
    form_class = forms.EmployerWithJointApplicantSignatureForm

    def form_valid(self, form):
        self.object = super().get_object()
        self.object.employer_signature_1 = form.cleaned_data.get('employer_signature')
        self.object.joint_applicant_signature = form.cleaned_data.get('joint_applicant_signature')
        self.object.save()
        return super().form_valid(form)

# Redirect Views

## Base View Class for all generate and revoke signature slug redirect views
class ModifySigSlugView(AgencyAccessToEmployerDocAppMixin, GetAuthorityMixin, RedirectView):
    model = models.CaseSignature
    pk_url_kwarg = 'level_1_pk'
    pattern_name = 'case_detail_route'
    stakeholder = ''
    view_type = ''
    
    def get_object(self):
        obj, created = self.model.objects.get_or_create(
            employer_doc__pk=self.kwargs.get(
                self.pk_url_kwarg
            ),
            defaults={
                'employer_doc': models.EmployerDoc.objects.get(
                    pk=self.kwargs.get(
                        self.pk_url_kwarg
                    )
                )
            }
        )
        return obj

    def get_redirect_url(self, *args, **kwargs):
        self.object = self.get_object()
        if self.view_type == 'generate':
            self.object.generate_sigslug(self.stakeholder)
        elif self.view_type == 'revoke':
            self.object.revoke_sigslug(self.stakeholder)
        kwargs={'level_1_pk': self.object.employer_doc.pk}
        return super().get_redirect_url(*args, **kwargs) + "#signatureUrlSection"

class GenerateSigSlugView(ModifySigSlugView):
    view_type = 'generate'

class RevokeSigSlugView(ModifySigSlugView):
    view_type = 'revoke'

class GenerateSigSlugEmployer1View(GenerateSigSlugView):
    stakeholder = 'employer_1'

class GenerateSigSlugEmployerSpouseView(GenerateSigSlugView):
    stakeholder = 'employer_spouse'

class GenerateSigSlugSponsor1View(GenerateSigSlugView):
    stakeholder = 'sponsor_1'

class GenerateSigSlugSponsor2View(GenerateSigSlugView):
    stakeholder = 'sponsor_2'

class GenerateSigSlugJointApplicantView(GenerateSigSlugView):
    stakeholder = 'joint_applicant'

class RevokeSigSlugEmployer1View(RevokeSigSlugView):
    stakeholder = 'employer_1'

class RevokeSigSlugEmployerSpouseView(RevokeSigSlugView):
    stakeholder = 'employer_spouse'

class RevokeSigSlugSponsor1View(RevokeSigSlugView):
    stakeholder = 'sponsor_1'

class RevokeSigSlugSponsor2View(RevokeSigSlugView):
    stakeholder = 'sponsor_2'

class RevokeSigSlugJointApplicantView(RevokeSigSlugView):
    stakeholder = 'joint_applicant'

class TokenChallengeView(
    SuccessMessageMixin,
    FormView,
):
    model = models.CaseSignature
    form_class = forms.TokenChallengeForm
    slug_url_kwarg = 'slug'
    template_name = 'employer_documentation/signature_challenge_form.html'
    stakeholder = ''

    def get_object(self):
        slug = self.kwargs.get(
            self.slug_url_kwarg
        )
        stakeholder = self.model.reverse_sigslug_header_dict.get(slug[0:5])
        if stakeholder:
            self.stakeholder = stakeholder
            try:
                if stakeholder == 'employer_1':
                    obj = self.model.objects.get(
                        sigslug_employer_1=slug
                    )
                elif stakeholder == 'employer_spouse':
                    obj = self.model.objects.get(
                        sigslug_employer_spouse=slug
                    )
                elif stakeholder == 'sponsor_1':
                    obj = self.model.objects.get(
                        sigslug_sponsor_1=slug
                    )
                elif stakeholder == 'sponsor_2':
                    obj = self.model.objects.get(
                        sigslug_sponsor_2=slug
                    )
                elif stakeholder == 'joint_applicant':
                    obj = self.model.objects.get(
                        sigslug_joint_applicant=slug
                    )
                else:
                    obj = None
                    return obj
            except self.model.DoesNotExist:
                obj = None
                return obj
            else:
                self.employer_doc_pk = obj.employer_doc.pk
                return obj
        else:
            # SLUG DOES NOT HAVE FRONT HEADER
            # TODO: Special Error Page thing
            pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('error_404'))

    def get_success_url(self) -> str:
        signature_route_dict = {
            # Stakeholder: View Url Name
            'employer_1':       'token_employer_signature_form_view',
            'employer_spouse':  'token_employer_spouse_signature_form_view',
            'sponsor_1':        'token_sponsor_1_signature_form_view',
            'sponsor_2':        'token_sponsor_2_signature_form_view',
            'joint_applicant':  'token_joint_applicant_signature_form_view'
        }
        return reverse(
            signature_route_dict[self.stakeholder],
            kwargs={
                'slug': getattr(self.get_object(), 'sigslug_' + self.stakeholder)
            }
        )

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs.update({
            'object': self.get_object(),
            'stakeholder': self.stakeholder
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
