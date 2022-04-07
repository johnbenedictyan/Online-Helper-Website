import uuid
from typing import Any, Dict, Optional, Type

from agency.mixins import GetAuthorityMixin
from agency.models import Agency
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet as QS
from django.forms.forms import BaseForm
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.http.request import HttpRequest as req
from django.http.response import HttpResponse as res
from django.shortcuts import get_object_or_404, redirect
from django.urls import resolve, reverse, reverse_lazy
from django.views.generic import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import View
from maid.helper_functions import is_maid_new
from onlinemaid.constants import AG_SALES
from onlinemaid.types import T, _FormT

from .constants import (ERROR_MESSAGES_VERBOSE_NAME_MAP,
                        monthly_income_label_map)
from .forms import (CaseStatusForm, ChallengeForm, DocSafetyAgreementForm,
                    DocServAgmtEmpCtrForm, DocServiceFeeScheduleForm,
                    DocUploadForm, EmployerDocForm, EmployerForm,
                    EmployerIncomeDetailsForm, EmployerJointApplicantForm,
                    EmployerSignatureForm, EmployerSponsorForm,
                    EmployerWithJointApplicantSignatureForm,
                    EmployerWithOneSponsorSignatureForm,
                    EmployerWithSpouseSignatureForm,
                    EmployerWithTwoSponsorSignatureForm, HandoverSignatureForm,
                    RemainingAmountDetailForm, SignatureForm)
from .formset import (EmployerHouseholdFormSet, EmployerHouseholdFormSetHelper,
                      MaidInventoryFormSet, MaidInventoryFormSetHelper)
from .helper_functions import (is_applicant_joint_applicant,
                               is_applicant_sponsor)
from .mixins import (AgencyAccessToEmployerDocAppMixin, EmployerDocAccessMixin,
                     OwnerAccessToEmployerDocAppMixin, PdfHtmlViewMixin)
from .models import (CaseSignature, CaseStatus, DocSafetyAgreement,
                     DocServAgmtEmpCtr, DocServiceFeeSchedule, DocUpload,
                     Employer, EmployerDoc, EmployerIncome,
                     EmployerJointApplicant, EmployerSponsor)

# Detail Views


class EmployerDetailView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DetailView,
):
    model = Employer
    pk_url_kwarg = 'level_0_pk'
    template_name = 'detail/dashboard-employer-detail.html'


class EmployerDocDetailView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'detail/dashboard-case-detail.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
    model = Employer
    form_class = EmployerForm
    template_name = 'crispy_form.html'

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE'
        })
        return kwargs

    def form_valid(self, form) -> res:
        if self.authority == AG_SALES:
            form.instance.agency_employee = self.request.user.agency_employee
        return super().form_valid(form)

    def get_success_url(self) -> str:
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
    model = EmployerSponsor
    form_class = EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.get_object().applicant_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def form_valid(self, form) -> res:
        form.instance.employer = self.get_object()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('employer_incomedetails_create_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })


class EmployerJointApplicantCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = EmployerJointApplicant
    form_class = EmployerJointApplicantForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.get_object().applicant_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form) -> res:
        form.instance.employer = self.get_object()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('employer_incomedetails_create_route', kwargs={
            'level_0_pk': self.object.employer.pk
        })


class EmployerIncomeDetailsCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = EmployerIncome
    form_class = EmployerIncomeDetailsForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.get_object().applicant_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
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

    def form_valid(self, form) -> res:
        form.instance.employer = self.get_object()
        return super().form_valid(form)

    def get_success_url(self) -> str:
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
    model = EmployerDoc
    form_class = EmployerDocForm
    template_name = 'crispy_form.html'

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'agency_id': self.agency_id
        })
        return kwargs

    def get_success_url(self) -> str:
        success_url = reverse_lazy('servicefee_create_route', kwargs={
            'level_1_pk': self.object.pk
        })
        return success_url


class DocServiceFeeScheduleCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = DocServiceFeeSchedule
    form_class = DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form) -> res:
        form.instance.employer_doc = self.get_object()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        self.object.set_deposit_invoice()
        success_url = reverse_lazy('serviceagreement_create_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url


class DocServAgmtEmpCtrCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = DocServAgmtEmpCtr
    form_class = DocServAgmtEmpCtrForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form) -> res:
        form.instance.employer_doc = self.get_object()
        return super().form_valid(form)

    def get_success_url(self) -> str:
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
    model = DocSafetyAgreement
    form_class = DocSafetyAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'CREATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form) -> res:
        form.instance.employer_doc = self.get_object()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        success_url = reverse_lazy('docupload_create_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url


class DocUploadCreateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    CreateView
):
    model = DocUpload
    form_class = DocUploadForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.get_object().fdw.maid_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def form_valid(self, form) -> res:
        form.instance.employer_doc = self.get_object()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('dashboard_case_list')

# Update Views


class EmployerUpdateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = Employer
    form_class = EmployerForm
    template_name = 'crispy_form.html'
    pk_url_kwarg = 'level_0_pk'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.object.applicant_type,
        })

        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE'
        })
        return kwargs

    def get_success_url(self) -> str:
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
    model = EmployerSponsor
    form_class = EmployerSponsorForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.object.employer.pk,
            'type_of_applicant': self.object.employer.applicant_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def get_success_url(self) -> str:
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
    model = EmployerJointApplicant
    form_class = EmployerJointApplicantForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.object.employer.applicant_type,
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
        })
        return kwargs

    def get_success_url(self) -> str:
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
    model = EmployerIncome
    form_class = EmployerIncomeDetailsForm
    pk_url_kwarg = 'level_0_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_0_pk': self.kwargs.get(self.pk_url_kwarg),
            'type_of_applicant': self.object.employer.applicant_type,
        })
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
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

    def get_success_url(self) -> str:
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
    model = EmployerDoc
    form_class = EmployerDocForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.object.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'agency_id': self.agency_id
        })
        return kwargs

    def get_success_url(self) -> str:
        success_url = reverse_lazy('servicefee_create_route', kwargs={
            'level_1_pk': self.object.pk
        })
        return success_url


class DocServiceFeeScheduleUpdateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = DocServiceFeeSchedule
    form_class = DocServiceFeeScheduleForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self) -> str:
        self.object.set_deposit_invoice()
        success_url = reverse_lazy('serviceagreement_create_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url


class DocServAgmtEmpCtrUpdateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = DocServAgmtEmpCtr
    form_class = DocServAgmtEmpCtrForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self) -> str:
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
    model = DocSafetyAgreement
    form_class = DocSafetyAgreementForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'form_type': 'UPDATE',
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self) -> str:
        success_url = reverse_lazy('docupload_create_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url


class DocUploadUpdateView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = DocUpload
    form_class = DocUploadForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self) -> str:
        return reverse('dashboard_case_list')


class CaseStatusUpdateView(GetAuthorityMixin, UpdateView):
    model = CaseStatus
    form_class = CaseStatusForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg),
            'maid_type': self.object.employer_doc.fdw.maid_type,
        })
        return context

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user_pk': self.request.user.pk,
            'authority': self.authority,
            'level_1_pk': self.kwargs.get(self.pk_url_kwarg)
        })
        return kwargs

    def get_success_url(self) -> str:
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
    model = Employer
    pk_url_kwarg = 'level_0_pk'
    template_name = 'employer_confirm_delete.html'
    success_url = 'dashboard_employers_list'


class EmployerDocDeleteView(
    OwnerAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    DeleteView
):
    model = EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'employer_confirm_delete.html'
    success_url = 'dashboard_case_list'


# Signature Views


class SignatureUpdateByAgentView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    UpdateView
):
    model = CaseSignature
    form_class = SignatureForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'signature_form_agency.html'
    model_field_name = None
    form_fields = None

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
        self.object = self.get_object()
        ed = self.object.employer_doc
        missing_details = ed.get_missing_case_dets_pre_signing_1()
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

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'model_field_name': self.model_field_name,
            'form_fields': self.form_fields
        })
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        model_field_verbose_name = CaseSignature._meta.get_field(
            self.model_field_name
        ).verbose_name
        context.update({
            'model_field_verbose_name': model_field_verbose_name
        })
        return context

    def get_success_url(self) -> str:
        return reverse_lazy('case_detail_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk,
        })

    def form_valid(self, form) -> res:
        self.object.employer_doc.set_status_wait_emp_sign()
        return super().form_valid(form)

# PDF Views


class HtmlToRenderPdfAgencyView(
    AgencyAccessToEmployerDocAppMixin,
    GetAuthorityMixin,
    PdfHtmlViewMixin,
    DetailView
):
    model = EmployerDoc
    pk_url_kwarg = 'level_1_pk'

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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
    model = EmployerDoc
    pk_url_kwarg = 'level_1_pk'

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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
    model = EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    as_attachment = False
    filename = 'document.pdf'
    field_name = None

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
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

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return Employer.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'employer_id': self.employer_id,
            'level_0_pk': self.kwargs.get(
                self.pk_url_kwarg
            ),
            'type_of_applicant': Employer.objects.get(
                pk=self.kwargs.get(
                    self.pk_url_kwarg
                )
            ).applicant_type
        })
        income_obj = Employer.objects.get(
            pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        ).get_income_obj()
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
        return Employer.objects.get(
            pk=self.employer_id
        )

    def get_form_kwargs(self) -> Dict[str, Any]:
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

    def form_valid(self, form) -> res:
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

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
        return EmployerDoc.objects.get(
            pk=self.employer_doc_id
        )

    def get_form_kwargs(self) -> Dict[str, Any]:
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

    def form_valid(self, form) -> res:
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
    http_method_names = ['get', 'post']
    template_name = 'signature_form.html'
    pk_url_kwarg = 'level_1_pk'
    form_type = None

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return EmployerDoc.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'object': self.object,
            'case_type': self.object.get_case_type()
        })
        return context

    def get_form_class(self) -> Type[_FormT]:
        self.object = self.get_object()
        case_type_form_class_map = {
            'SINGLE': EmployerSignatureForm,
            'SPOUSE': EmployerWithSpouseSignatureForm,
            'SPONSR1': EmployerWithOneSponsorSignatureForm,
            'SPONSR2': EmployerWithTwoSponsorSignatureForm,
            'JNT_AP': EmployerWithJointApplicantSignatureForm,
        }
        return case_type_form_class_map[self.object.get_case_type()]

    def get_success_url(self) -> str:
        return reverse(
            'employer_document_detail', kwargs={
                'level_1_pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            })

    def form_valid(self, form) -> res:
        case_type = self.object.get_case_type()
        signature_obj = self.object.rn_signatures_ed
        signature_obj.employer_signature_1 = form.cleaned_data.get(
            'employer_signature'
        )
        if case_type == 'SINGLE':
            signature_obj.save()
        if case_type == 'SPOUSE':
            signature_obj.employer_spouse_signature = form.cleaned_data.get(
                'employer_spouse_signature'
            )
            signature_obj.save()
        elif case_type == 'SPONSR1':
            signature_obj.sponsor_1_signature = form.cleaned_data.get(
                'employer_sponsor1_signature'
            )
            signature_obj.save()
        elif case_type == 'SPONSR2':
            signature_obj.sponsor_1_signature = form.cleaned_data.get(
                'employer_sponsor1_signature'
            )
            signature_obj.sponsor_2_signature = form.cleaned_data.get(
                'employer_sponsor2_signature'
            )
            signature_obj.save()
        elif case_type == 'JNT_AP':
            signature_obj.joint_applicant_signature = form.cleaned_data.get(
                'joint_applicant_signature'
            )
            signature_obj.save()
        self.object.set_status_wait_to_handover()
        return super().form_valid(form)


class EmployerDocumentDetailView(EmployerDocAccessMixin, DetailView):
    model = EmployerDoc
    pk_url_kwarg = 'level_1_pk'
    template_name = 'documents.html'


class HandoverFormView(FormView):
    model = CaseSignature
    form_class = HandoverSignatureForm
    pk_url_kwarg = 'level_1_pk'
    http_method_names = ['get', 'post']
    template_name = 'signature_form_handover.html'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return self.model.objects.get(
            employer_doc__pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({
            'object': self.object
        })
        return context

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
        self.object = self.get_object()
        ed = self.object.employer_doc
        missing_details = ed.get_missing_case_dets_pre_signing_2()
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

    def get_success_url(self) -> str:
        return reverse_lazy('dashboard_case_list')

    def form_valid(self, form) -> res:
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
            self.object.employer_doc.set_archive()
        except Exception as e:
            print(e)
        else:
            self.object.employer_doc.delete()

        return super().form_valid(form)

# Redirect Views


class ArchiveCase(RedirectView):
    http_method_names = ['get']
    pattern_name = 'dashboard_case_list'

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> Optional[str]:
        return super().get_redirect_url(*args, **kwargs)


class CaseStatusAPIView(View):
    def get(self, request: req, *args: str, **kwargs: Any) -> res:
        data = {}
        try:
            case_status = CaseStatus.objects.get(
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
    model = DocServiceFeeSchedule
    form_class = RemainingAmountDetailForm
    http_method_names = ['get', 'post']
    pk_url_kwarg = 'level_1_pk'
    template_name = 'crispy_form.html'
    success_url = reverse_lazy('dashboard_sales_list')

    def get_queryset(self) -> QS[T]:
        return DocServiceFeeSchedule.objects.get(
            employer_doc__pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        )

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return DocServiceFeeSchedule.objects.get(
            employer_doc__pk=self.kwargs.get(
                self.pk_url_kwarg
            )
        )

    def form_valid(self, form: RemainingAmountDetailForm):
        return super().form_valid(form)

    def get_success_url(self) -> str:
        self.object.set_remaining_invoice()
        success_url = reverse_lazy('case_detail_route', kwargs={
            'level_1_pk': self.object.employer_doc.pk
        })
        return success_url


class ChallengeFormView(SuccessMessageMixin, FormView):
    model = EmployerDoc
    form_class = ChallengeForm
    pk_url_kwarg = 'level_1_pk'
    template_name = 'signature_challenge_form.html'
    success_url = 'potential_employer_detail'

    def get_object(self, queryset: Optional[QS] = ...) -> T:
        return get_object_or_404(
            EmployerDoc,
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get(self, request: req, *args: str, **kwargs: Any) -> res:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self) -> Dict[str, Any]:
        self.object = self.get_object()
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'object': self.object
        })
        return kwargs

    def get_success_url(self) -> str:
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        else:
            return super().get_success_url()

    def form_valid(self, form: BaseForm) -> res:
        index_uuid = str(uuid.uuid5(
            uuid.UUID(settings.ACCOUNT_UUID_NAMESPACE),
            str(self.request.user.pk)
        ))
        if self.request.session.get(
            index_uuid,
            None
        ):
            old_list = self.request.session[index_uuid]
            new_list = old_list.append(str(self.object.key_uuid))
            self.request.session[index_uuid] = new_list
        else:
            self.request.session[index_uuid] = list()
            self.request.session[index_uuid].append(str(self.object.key_uuid))
        return super().form_valid(form)
