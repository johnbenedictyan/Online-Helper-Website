# Django
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http.response import HttpResponse
from django.urls import reverse, reverse_lazy, resolve
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import RedirectView
from django.views.generic.list import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView, FormView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect

from agency.models import Agency
from agency.mixins import GetAuthorityMixin
from maid.helper_functions import is_maid_new
from onlinemaid.constants import AG_SALES

# From our apps
from . import models, forms
from .constants import (
    monthly_income_label_map, ERROR_MESSAGES_VERBOSE_NAME_MAP
)
from .formset import (
    EmployerHouseholdFormSet, EmployerHouseholdFormSetHelper,
    MaidInventoryFormSet, MaidInventoryFormSetHelper
)
from .helper_functions import (
    is_applicant_joint_applicant, is_applicant_sponsor
)
from .mixins import (
    EmployerDocAccessMixin, PdfHtmlViewMixin,
    AgencyAccessToEmployerDocAppMixin, OwnerAccessToEmployerDocAppMixin
)

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
            'agency_name': Agency.objects.get(
                pk=self.agency_id
            ).name
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
    template_name = 'crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE'
        })
        return kwargs

    def form_valid(self, form):
        if self.authority == AG_SALES:
            form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

    def get_success_url(self):
        if is_applicant_sponsor(self.object.applicant_type):
            success_url = reverse_lazy(
                'employer_sponsor_create_route',
                kwargs={
                    'level_0_pk': self.object.pk
                }
            )

        elif is_applicant_joint_applicant(self.object.applicant_type):
            success_url = reverse_lazy(
                'employer_jointapplicant_create_route',
                kwargs={
                    'level_0_pk': self.object.pk
                }
            )

        else:
            success_url = reverse_lazy(
                'employer_incomedetails_create_route',
                kwargs={
                    'level_0_pk': self.object.pk
                }
            )

        return success_url


class EmployerSponsorCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
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
        if not is_applicant_sponsor(self.object.applicant_type):
            return HttpResponseRedirect(
                reverse(
                    'employer_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        elif hasattr(self.object, 'rn_sponsor_employer'):
            return HttpResponseRedirect(
                reverse(
                    'employer_sponsor_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def form_valid(self, form):
        form.instance.employer = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_incomedetails_create_route', kwargs={
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
    template_name = 'crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
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
        if not is_applicant_joint_applicant(self.object.applicant_type):
            return HttpResponseRedirect(
                reverse(
                    'employer_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        elif hasattr(self.object, 'rn_ja_employer'):
            return HttpResponseRedirect(
                reverse(
                    'employer_jointapplicant_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def form_valid(self, form):
        form.instance.employer = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employer_incomedetails_create_route', kwargs={
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
    template_name = 'crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
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
                reverse(
                    'employer_incomedetails_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        type_of_applicant = self.get_object().applicant_type
        monthly_income_label = monthly_income_label_map.get(
            type_of_applicant
        )
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'monthly_income_label': monthly_income_label,
            'form_type': 'CREATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def form_valid(self, form):
        form.instance.employer = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.employer.household_details_required:
            return reverse_lazy('employer_householddetails_route', kwargs={
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
    template_name = 'crispy_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'agency_id': self.agency_id
        })
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('servicefee_create_route', kwargs={
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
    template_name = 'crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
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
                reverse(
                    'servicefee_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        self.object.generate_deposit_invoice()
        success_url = reverse_lazy('serviceagreement_create_route', kwargs={
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
    template_name = 'crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
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
                reverse(
                    'serviceagreement_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.get_object()
        return super().form_valid(form)

    def get_success_url(self):
        if is_maid_new(self.object.employer_doc.fdw.maid_type):
            success_url = reverse_lazy('safetyagreement_create_route', kwargs={
                'level_1_pk': self.object.employer_doc.pk
            })
        else:
            success_url = reverse_lazy('docupload_create_route', kwargs={
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
    template_name = 'crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
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
                reverse(
                    'safetyagreement_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.get_object()

        return super().form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy('docupload_create_route', kwargs={
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
    template_name = 'crispy_form.html'

    def get_object(self, *args, **kwargs):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
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
                reverse(
                    'docupload_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form):
        form.instance.employer_doc = self.get_object()
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
    template_name = 'crispy_form.html'
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
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE'
        })
        return kwargs

    def get_success_url(self):
        if is_applicant_sponsor(self.object.applicant_type):
            success_url = reverse_lazy(
                'employer_sponsor_create_route',
                kwargs={
                    'level_0_pk': self.object.pk
                }
            )
        elif is_applicant_joint_applicant(self.object.applicant_type):
            success_url = reverse_lazy(
                'employer_jointapplicant_create_route',
                kwargs={
                    'level_0_pk': self.object.pk
                }
            )
        else:
            success_url = reverse_lazy(
                'employer_incomedetails_create_route',
                kwargs={
                    'level_0_pk': self.object.pk
                }
            )
        return success_url


class EmployerSponsorUpdateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerSponsor
    form_class = forms.EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not is_applicant_sponsor(self.object.employer.applicant_type):
            return HttpResponseRedirect(
                reverse(
                    'employer_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy(
            'employer_incomedetails_create_route',
            kwargs={
                'level_0_pk': self.object.employer.pk
            }
        )
        return success_url


class EmployerDocJointApplicantUpdateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerJointApplicant
    form_class = forms.EmployerJointApplicantForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not is_applicant_joint_applicant(
            self.object.employer.applicant_type
        ):
            return HttpResponseRedirect(
                reverse(
                    'employer_update_route',
                    kwargs={
                        self.pk_url_kwarg: self.kwargs.get(self.pk_url_kwarg)
                    }
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy(
            'employer_incomedetails_create_route',
            kwargs={
                'level_0_pk': self.object.employer.pk
            }
        )
        return success_url


class EmployerIncomeDetailsUpdateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.EmployerIncome
    form_class = forms.EmployerIncomeDetailsForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

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
        type_of_applicant = self.object.employer.applicant_type
        monthly_income_label = monthly_income_label_map.get(
            type_of_applicant
        )
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'monthly_income_label': monthly_income_label,
            'form_type': 'UPDATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def get_success_url(self):
        if self.object.employer.household_details_required:
            success_url = reverse_lazy(
                'employer_householddetails_route',
                kwargs={
                    'level_0_pk': self.object.employer.pk
                }
            )
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
    template_name = 'crispy_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.object.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'agency_id': self.agency_id
        })
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('servicefee_create_route', kwargs={
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
    template_name = 'crispy_form.html'

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
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self):
        self.object.generate_deposit_invoice()
        success_url = reverse_lazy('serviceagreement_create_route', kwargs={
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
    template_name = 'crispy_form.html'

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
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self):
        if is_maid_new(self.object.employer_doc.fdw.maid_type):
            success_url = reverse_lazy('safetyagreement_create_route', kwargs={
                'level_1_pk': self.object.employer_doc.pk
            })
        else:
            success_url = reverse_lazy('docupload_create_route', kwargs={
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
    template_name = 'crispy_form.html'

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
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self):
        success_url = reverse_lazy('docupload_create_route', kwargs={
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
    template_name = 'crispy_form.html'

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
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self):
        return reverse('dashboard_case_list')


class CaseStatusUpdateView(GetAuthorityMixin, UpdateView):
    model = models.CaseStatus
    form_class = forms.CaseStatusForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

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
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
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
            return reverse_lazy('safetyagreement_create_route', kwargs={
                'level_1_pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            })

# Delete Views


class EmployerDeleteView(
    OwnerAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DeleteView
):
    model = models.Employer
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_confirm_delete.html'
    success_url = 'dashboard_employers_list'


class EmployerDocDeleteView(
    OwnerAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DeleteView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_confirm_delete.html'
    success_url = 'dashboard_case_list'


# Signature Views


class SignatureUpdateByAgentView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = models.CaseSignature
    form_class = forms.SignatureForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'signature_form_agency.html'
    model_field_name = None
    form_fields = None

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'model_field_name': self.model_field_name,
            'form_fields': self.form_fields
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_field_verbose_name = models.CaseSignature._meta.get_field(
            self.model_field_name
        ).verbose_name
        context.update({
            'model_field_verbose_name': model_field_verbose_name
        })
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
            context.update({
                'repayment_table': self.calc_repayment_schedule()
            })

        context.update({
            'url_name': request.resolver_match.url_name
        })
        return self.generate_pdf_response(request, context)


class HtmlToRenderPdfEmployerView(
    EmployerDocAccessMixin,
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
            context.update({
                'repayment_table': self.calc_repayment_schedule()
            })

        context.update({
            'url_name': request.resolver_match.url_name
        })
        return self.generate_pdf_response(request, context)


class UploadedPdfAgencyView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DetailView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    as_attachment = False
    filename = 'document.pdf'
    field_name = None

    def get_object(self):
        return self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return FileResponse(
                getattr(self.object.rn_docupload_ed, self.field_name).open(),
                as_attachment=self.as_attachment,
                filename=self.filename,
                content_type='application/pdf'
            )
        except Exception:
            return HttpResponseRedirect(
                reverse(
                    'docupload_create_route',
                    kwargs={
                        'level_1_pk': self.object.pk,
                    }
                )
            )


# Form Views


class EmployerHouseholdDetailsFormView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    SuccessMessageMixin,
    FormView
):
    form_class = EmployerHouseholdFormSet
    http_method_names = ['get', 'post']
    template_name = 'crispy_form.html'
    pk_url_kwarg = 'level_0_pk'
    authority = ''
    agency_id = ''
    employer_id = ''
    success_message = 'Household details updated'

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
            'type_of_applicant': models.Employer.objects.get(
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
                    'employer_householddetails_route',
                    kwargs={
                        'level_0_pk': self.employer_id
                    }
                )
            )

    def get_success_url(self) -> str:
        return reverse_lazy(
            'dashboard_employers_list'
        )


class MaidInventoryFormView(AgencyAccessToEmployerDocAppMixin,
                            GetAuthorityMixin, SuccessMessageMixin, FormView):
    form_class = MaidInventoryFormSet
    http_method_names = ['get', 'post']
    template_name = 'crispy_form.html'
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
            ),
            'maid_type': self.get_object().fdw.maid_type
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
                    'maid_inventory_route',
                    kwargs={
                        'level_1_pk': self.employer_doc_id
                    }
                )
            )

    def get_success_url(self) -> str:
        return reverse_lazy(
            'docupload_create_route',
            kwargs={
                'level_1_pk': self.employer_doc_id
            }
        )


class SignatureFormView(EmployerDocAccessMixin, FormView):
    slug_url_kwarg = 'slug'
    http_method_names = ['get', 'post']
    template_name = 'signature_form.html'
    pk_url_kwarg = 'level_1_pk'
    form_type = None

    def get_object(self):
        return models.EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object': self.object,
            'case_type': self.object.get_case_type()
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_form_class(self):
        case_type_form_class_map = {
            'SINGLE': forms.EmployerSignatureForm,
            'SPOUSE': forms.EmployerWithSpouseSignatureForm,
            'SPONSR1': forms.EmployerWithOneSponsorForm,
            'SPONSR2': forms.EmployerWithTwoSponsorForm,
            'JNT_AP': forms.EmployerWithJointApplicantSignatureForm,
        }
        return case_type_form_class_map[self.object.get_case_type()]

    def get_success_url(self):
        return reverse(
            'pdf_signed_documents', kwargs={
                'slug': self.kwargs.get(
                    self.slug_url_kwarg
                )
            })

    def form_valid(self, form) -> HttpResponse:
        case_type = self.object.get_case_type()
        self.object.employer_signature_1 = form.cleaned_data.get(
            'employer_signature'
        )
        if case_type == 'SINGLE':
            self.object.save()
        if case_type == 'SPOUSE':
            self.object.employer_spouse_signature = form.cleaned_data.get(
                'employer_spouse_signature'
            )
            self.object.save()
        elif case_type == 'SPONSR1':
            self.object.sponsor_1_signature = form.cleaned_data.get(
                'employer_sponsor1_signature'
            )
            self.object.save()
        elif case_type == 'SPONSR2':
            self.object.sponsor_1_signature = form.cleaned_data.get(
                'employer_sponsor1_signature'
            )
            self.object.sponsor_2_signature = form.cleaned_data.get(
                'employer_sponsor2_signature'
            )
            self.object.save()
        elif case_type == 'JNT_AP':
            self.object.joint_applicant_signature = form.cleaned_data.get(
                'joint_applicant_signature'
            )
            self.object.save()
        return super().form_valid(form)


class EmployerDocumentDetailView(EmployerDocAccessMixin, DetailView):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'documents.html'


class HandoverFormView(FormView):
    model = models.CaseSignature
    form_class = forms.HandoverSignatureForm
    pk_url_kwarg = 'level_1_pk'
    http_method_names = ['get', 'post']
    template_name = 'signature_form_handover.html'

    def get_object(self):
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object': self.object
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        ed = self.object.employer_doc
        missing_details = ed.details_missing_case_pre_signing_2()
        if missing_details:
            for md in missing_details:
                messages.warning(
                    self.request,
                    ERROR_MESSAGES_VERBOSE_NAME_MAP[md],
                    extra_tags='error'
                )
            return redirect(
                reverse(
                    'case_detail_route',
                    kwargs={
                        'level_1_pk': self.object.employer_doc.pk
                    }
                )
            )

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('dashboard_case_list')

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.employer_signature_2 = form.cleaned_data.get(
            'employer_signature'
        )
        self.object.fdw_signature = form.cleaned_data.get('fdw_signature')
        self.object.agency_staff_signature = form.cleaned_data.get(
            'agency_employee_signature'
        )
        self.object.save()

        try:
            self.object.employer_doc.archive()
        except Exception as e:
            print(e)
        else:
            self.object.employer_doc.delete()

        return super().form_valid(form)

# Redirect Views


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


class GenerateRemainingAmountDepositReceipt(UpdateView):
    model = models.DocServiceFeeSchedule
    form_class = forms.RemainingAmountDetailForm
    http_method_names = ['get', 'post']
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'
    success_url = reverse_lazy('dashboard_sales_list')

    def get_queryset(self):
        return models.DocServiceFeeSchedule.objects.get(
            employer_doc__pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        )

    def get_object(self):
        return models.DocServiceFeeSchedule.objects.get(
            employer_doc__pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        )

    def form_valid(self, form: forms.RemainingAmountDetailForm):
        return super().form_valid(form)

    def get_success_url(self):
        self.object.generate_remaining_invoice()
        success_url = reverse_lazy('case_detail_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url
