# Django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django.http import FileResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.generic import RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile

# From our apps
from agency.mixins import AgencyLoginRequiredMixin, GetAuthorityMixin
from . import models, forms, constants
from .formset import EmployerHouseholdFormSet, EmployerHouseholdFormSetHelper
from .mixins import *
from onlinemaid import constants as om_constants
from maid import constants as maid_constants

# Start of Views

# List Views
# class EmployerListView(
#     AgencyLoginRequiredMixin,
#     GetAuthorityMixin,
#     ListView
# ):
#     model = models.Employer
#     ordering = ['employer_name']
#     paginate_by = 20

#     def get_queryset(self):
#         search_terms = self.request.GET.get('search')

#         # Filter results by user's search terms
#         if search_terms:
#             queryset = super().get_queryset().filter(
#                 Q(employer_name__icontains=search_terms) |
#                 Q(employer_email__icontains=search_terms) |
#                 Q(employer_mobile_number__icontains=search_terms)
#             )
#         else:
#             queryset = super().get_queryset()

#         # Further filter queryset to only show the employers that current user
#         # has necessary permission to access
#         if self.authority==om_constants.AG_OWNERS:
#             # If agency owner, return all employers belonging to agency
#             return queryset.filter(
#                 agency_employee__agency
#                 = self.request.user.agency_owner.agency
#             )
#         elif self.authority==om_constants.AG_ADMINS:
#             # If agency administrator, return all employers belonging to agency
#             return queryset.filter(
#                 agency_employee__agency
#                 = self.request.user.agency_employee.agency
#             )
#         elif self.authority==om_constants.AG_MANAGERS:
#             # If agency manager, return all employers belonging to branch
#             return queryset.filter(
#                 agency_employee__branch
#                 = self.request.user.agency_employee.branch
#             )
#         elif self.authority==om_constants.AG_SALES:
#             # If agency owner, return all employers belonging to self
#             return queryset.filter(
#                 agency_employee = self.request.user.agency_employee
#             )
#         else:
#             return self.handle_no_permission()

# class DocListView(
#     AgencyLoginRequiredMixin,
#     GetAuthorityMixin,
#     ListView
# ):
#     model = models.EmployerDoc
#     # template_name = 'employer_documentation/sales_list.html'
#     ordering = ['-agreement_date']
#     paginate_by = 20
#     is_deployed = None

#     def get_queryset(self):
#         search_terms = self.request.GET.get('search')
#         start_date = self.request.GET.get('start_date')
#         end_date = self.request.GET.get('end_date')
#         sort_by = self.request.GET.get('sort_by')

#         # Sort by dates
#         if sort_by:
#             # Get field to sort by
#             if 'agreement_date' in sort_by:
#                 sort_field_name = 'agreement_date'
#             elif 'fdw_work_commencement_date' in sort_by:
#                 sort_field_name = 'rn_casestatus_ed__fdw_work_commencement_date'
#             elif 'ipa_date' in sort_by:
#                 sort_field_name = 'rn_casestatus_ed__ipa_approval_date'
        
#             # Get ascending or descending user selection
#             if sort_by.endswith('asc'):
#                 self.ordering = [sort_field_name]
#             elif sort_by.endswith('des'):
#                 self.ordering = ['-' + sort_field_name]
#         else:
#             sort_field_name = self.ordering[0].replace('-', '')

#         # Get queryset
#         queryset = super().get_queryset().filter(
#             rn_casestatus_ed__is_deployed=self.is_deployed
#         )

#         # Filter results by user's search terms
#         if search_terms:
#             queryset = queryset.filter(
#                 Q(case_ref_no__icontains=search_terms) |
#                 Q(employer__employer_name__icontains=search_terms) |
#                 Q(employer__employer_email__icontains=search_terms) |
#                 Q(employer__employer_mobile_number__icontains=search_terms)
#             )
        
#         # Further filter queryset to only show the employers that current user
#         # has necessary permission to access
#         if self.authority==om_constants.AG_OWNERS:
#             # If agency owner, return all employers belonging to agency
#             queryset = queryset.filter(
#                 employer__agency_employee__agency
#                 = self.request.user.agency_owner.agency
#             )
#         elif self.authority==om_constants.AG_ADMINS:
#             # If agency administrator, return all employers belonging to agency
#             queryset = queryset.filter(
#                 employer__agency_employee__agency
#                 = self.request.user.agency_employee.agency
#             )
#         elif self.authority==om_constants.AG_MANAGERS:
#             # If agency manager, return all employers belonging to branch
#             queryset = queryset.filter(
#                 employer__agency_employee__branch
#                 = self.request.user.agency_employee.branch
#             )
#         elif self.authority==om_constants.AG_SALES:
#             # If agency owner, return all employers belonging to self
#             queryset = queryset.filter(
#                 employer__agency_employee = self.request.user.agency_employee
#             )
#         else:
#             return self.handle_no_permission()

#         # Filter by start and end dates from user input
#         if start_date:
#             start_date_kwargs = {sort_field_name+'__gte': start_date}
#             queryset = queryset.filter(**start_date_kwargs)
#         if end_date:
#             end_date_kwargs = {sort_field_name+'__lte': end_date}
#             queryset = queryset.filter(**end_date_kwargs)

#         return queryset

# class EmployerDocListView(
#     AgencyLoginRequiredMixin,
#     GetAuthorityMixin,
#     ListView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_0_pk'
#     ordering = ['-agreement_date']

#     def get_object(self, *args, **kwargs):
#         return models.Employer.objects.get(pk = self.kwargs.get(self.pk_url_kwarg))

#     def get_queryset(self):
#         return super().get_queryset().filter(employer=self.kwargs.get(
#             self.pk_url_kwarg))

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object(*args, **kwargs)
#         if self.object.rn_ed_employer.filter(employer=self.object.pk).count():
#             return super().get(request, *args, **kwargs)
#         else:
#             return HttpResponseRedirect(
#                 reverse(
#                     'case_create_route',
#                     kwargs={'level_0_pk': self.object.pk}
#                 )
#             )

# Detail Views
class EmployerDetailView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    DetailView,
):
    model = models.Employer
    pk_url_kwarg = 'level_0_pk'

class EmployerDocDetailView(
    AgencyLoginRequiredMixin,
    GetAuthorityMixin,
    DetailView
):
    model = models.EmployerDoc
    pk_url_kwarg = 'level_1_pk'

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
        return reverse_lazy('employer_incomedetails_create_route', kwargs={
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
        return reverse_lazy('employer_incomedetails_create_route', kwargs={
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
        return models.Employer.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
                )
            )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_pk'] = self.request.user.pk
        kwargs['authority'] = self.authority
        return kwargs

    def form_valid(self, form):
        form.instance.employer = models.Employer.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
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
        return reverse_lazy('dashboard_case_list')

# class EmployerDocSigSlugUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocSig
#     form_class = EmployerDocSigSlugForm
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

# class EmployerDocMaidStatusUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocMaidStatus
#     form_class = EmployerDocMaidStatusForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/crispy_form.html'

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['authority'] = self.authority
#         return kwargs

#     def get_success_url(self):
#         return reverse_lazy('ed_detail_route', kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#         })

# class EmployerDocMaidDeploymentUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocMaidStatus
#     form_class = EmployerDocMaidDeploymentForm
#     pk_url_kwarg = 'level_2_pk'

#     def get_success_url(self):
#         if self.object.is_deployed:
#             return reverse_lazy('dashboard_status_list')
#         else:
#             return reverse_lazy('dashboard_sales_list')

# class JobOrderUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     UpdateView
# ):
#     model = JobOrder
#     form_class = JobOrderForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/joborder_form.html'
#     success_url = reverse_lazy('dashboard_employers_list')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['authority'] = self.authority
#         return kwargs

#     def get_success_url(self):
#         return reverse_lazy('ed_detail_route', kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#         })

# class EmployerPaymentTransactionUpdateView(
#     CheckAgencyEmployeePermissionsMixin,
#     UpdateView
# ):
#     model = EmployerPaymentTransaction
#     form_class = EmployerPaymentTransactionForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/crispy_form.html'
#     success_url = reverse_lazy('dashboard_sales_list')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['user_pk'] = self.request.user.pk
#         kwargs['authority'] = self.authority
#         return kwargs


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
# class SignatureUpdateByAgentView(
#     CheckAgencyEmployeePermissionsMixin,
#     UpdateView
# ):
#     model = models.EmployerDocSig
#     form_class = SignatureForm
#     pk_url_kwarg = 'level_2_pk'
#     template_name = 'employer_documentation/signature_form_agency.html'
#     model_field_name = None
#     form_fields = None

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['model_field_name'] = self.model_field_name
#         kwargs['form_fields'] = self.form_fields
#         return kwargs

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['model_field_verbose_name'] = EmployerDocSig._meta.get_field(
#             self.model_field_name).verbose_name
#         return context

#     def get_success_url(self):
#         return reverse_lazy('ed_detail_route', kwargs={
#             'level_0_pk': self.object.employer_doc.employer.pk,
#             'level_1_pk': self.object.employer_doc.pk,
#         })

# class VerifyUserTokenView(
#     SuccessMessageMixin,
#     UpdateView
# ):
#     model = models.EmployerDocSig
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
#                 slug = self.object.employer_slug
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
#     model = models.EmployerDocSig
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
#         context['model_field_verbose_name'] = EmployerDocSig._meta.get_field(
#             self.model_field_name).verbose_name
#         return context

#     def get_success_url(self):
#         if self.success_url_route_name:
#             if self.token_field_name=='employer_token':
#                 slug = self.object.employer_slug
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
# class PdfGenericAgencyView(
#     CheckAgencyEmployeePermissionsMixin,
#     PdfHtmlViewMixin,
#     DetailView
# ):
#     model = models.EmployerDoc
#     pk_url_kwarg = 'level_1_pk'

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data()

#         if self.use_repayment_table:
#             context['repayment_table'] = self.calc_repayment_schedule()
        
#         context['url_name'] = request.resolver_match.url_name
#         return self.generate_pdf_response(request, context)

# class PdfFileAgencyView(
#     CheckAgencyEmployeePermissionsMixin,
#     DetailView
# ):
#     # model = None # To be passed as parameter in urls.py
#     # pk_url_kwarg = None # To be passed as parameter in urls.py
#     # slug_url_kwarg = None # To be passed as parameter in urls.py
#     as_attachment=False
#     filename='document.pdf'
#     field_name = None

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if isinstance(self.object, JobOrder):
#             try:
#                 return FileResponse(
#                     self.object.job_order_pdf.open(),
#                     as_attachment=self.as_attachment,
#                     filename=self.filename,
#                     content_type='application/pdf'
#                 )
#             except Exception:
#                 return HttpResponseRedirect(
#                     reverse('joborder_update_route', kwargs={
#                         'level_0_pk': self.object.employer_doc.employer.pk,
#                         'level_1_pk': self.object.employer_doc.pk,
#                         'level_2_pk': self.object.pk,
#                 }))
#         elif isinstance(self.object, EmployerDoc):
#             try:
#                 return FileResponse(
#                     getattr(self.object.rn_pdfarchive_ed, self.field_name).open(),
#                     as_attachment=self.as_attachment,
#                     filename=self.filename,
#                     content_type='application/pdf'
#                 )
#             except Exception:
#                 return HttpResponseRedirect(
#                     reverse('pdf_archive_detail', kwargs={
#                         'level_0_pk': self.object.employer.pk,
#                         'level_1_pk': self.object.pk,
#                 }))

# class PdfGenericTokenView(
#     CheckSignatureSessionTokenMixin,
#     PdfHtmlViewMixin,
#     DetailView
# ):
#     model = models.EmployerDocSig
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
#     model = models.EmployerDocSig
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
#     CheckAgencyEmployeePermissionsMixin,
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
#     CheckAgencyEmployeePermissionsMixin,
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

class ArchiveCase(RedirectView):
    http_method_names = ['get']
    pattern_name = 'dashboard_case_list'

    def get_redirect_url(self, *args, **kwargs):
        return super().get_redirect_url(*args, **kwargs)