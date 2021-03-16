# Imports from python
import json
from random import shuffle

# Imports from django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView, FormView, UpdateView, DeleteView
)

# Imports from project-wide files
from onlinemaid.mixins import ListFilteredMixin, SuccessMessageMixin

# Imports from foreign installed apps
from agency.models import Agency
from agency.mixins import AgencyLoginRequiredMixin, GetAuthorityMixin
from employer_documentation.mixins import PdfHtmlViewMixin

# Imports from local app
from .filters import MaidFilter
from .mixins import (
    SpecificAgencyMaidLoginRequiredMixin, SpecificAgencyOwnerRequiredMixin,
    FDWLimitMixin
)

from .forms import (
    MaidCreationForm, MaidPersonalDetailsForm, MaidFamilyDetailsForm, 
    MaidInfantChildCareForm, MaidElderlyCareForm, MaidDisabledCareForm,
    MaidGeneralHouseworkForm, MaidCookingForm, MaidFoodHandlingPreferenceForm,
    MaidDietaryRestrictionForm, MaidEmploymentHistoryForm, MaidUpdateForm, 
    MainMaidCreationForm, MaidCareForm, MaidFinancialDetailsForm, 
    MaidAgencyFeeTransactionForm
)

from .models import (
    Maid, MaidPersonalDetails, MaidFamilyDetails, MaidInfantChildCare, 
    MaidElderlyCare, MaidDisabledCare, MaidGeneralHousework, MaidCooking, 
    MaidFoodHandlingPreference, MaidDietaryRestriction, MaidEmploymentHistory,
    MaidAgencyFeeTransaction, MaidFinancialDetails, MaidOtherCare
)

from .mixins import SpecificAgencyMaidLoginRequiredMixin

# Start of Views

# Template Views

# Form Views
class MaidCreateFormView(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                         FDWLimitMixin, SuccessMessageMixin, FormView):
    form_class = MainMaidCreationForm
    http_method_names = ['get','post']
    success_url = reverse_lazy('dashboard_maid_detail')
    template_name = 'form/maid-create-form.html'
    authority = ''
    agency_id = ''
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id
        })
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk':self.object.pk
            }
        )
    
    def form_valid(self, form):
        agency = Agency.objects.get(
            pk=self.agency_id
        )
        if agency.amount_of_biodata < agency.amount_of_biodata_allowed:
            try:
                self.object = form.save()
            except Exception as e:
                messages.warning(
                    self.request,
                    'Please try again',
                    extra_tags='warning'
                )
                return super().form_invalid(form)
            else:
                return super().form_valid(form)
        else:
            messages.warning(
                self.request,
                'You have reached the limit of biodata',
                extra_tags='warning'
            )
            return super().form_invalid(form)

class MaidCareDetailsUpdate(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                 SuccessMessageMixin, FormView):
    form_class = MaidCareForm
    http_method_names = ['get','post']
    success_url = reverse_lazy('dashboard_maid_detail')
    template_name = 'update/maid-care.html'
    authority = ''
    agency_id = ''
    maid_id = None

    def get_initial(self):
        initial = super().get_initial()
        self.maid_id = self.kwargs.get('pk')
        maid = Maid.objects.get(
            pk=self.maid_id
        )
        initial.update({
            'skills_evaluation_method': maid.skills_evaluation_method,
            'cfi_assessment': maid.infant_child_care.assessment,
            'cfi_willingness': maid.infant_child_care.willingness,
            'cfi_experience': maid.infant_child_care.experience,
            'cfi_remarks': maid.infant_child_care.remarks,
            'cfi_other_remarks': maid.infant_child_care.other_remarks,
            'cfe_assessment': maid.elderly_care.assessment,
            'cfe_willingness': maid.elderly_care.willingness,
            'cfe_experience': maid.elderly_care.experience,
            'cfe_remarks': maid.elderly_care.remarks,
            'cfe_other_remarks': maid.elderly_care.other_remarks,
            'cfd_assessment': maid.disabled_care.assessment,
            'cfd_willingness': maid.disabled_care.willingness,
            'cfd_experience': maid.disabled_care.experience,
            'cfd_remarks': maid.disabled_care.remarks,
            'cfd_other_remarks': maid.disabled_care.other_remarks,
            'geh_assessment': maid.general_housework.assessment,
            'geh_willingness': maid.general_housework.willingness,
            'geh_experience': maid.general_housework.experience,
            'geh_remarks': maid.general_housework.remarks,
            'geh_other_remarks': maid.general_housework.other_remarks,
            'cok_assessment': maid.cooking.assessment,
            'cok_willingness': maid.cooking.willingness,
            'cok_experience': maid.cooking.experience,
            'cok_remarks': maid.cooking.remarks,
            'cok_other_remarks': maid.cooking.other_remarks,
            'care_for_pets': maid.other_care.care_for_pets,
            'gardening': maid.other_care.gardening
        })
        return initial

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        Maid.objects.filter(
            pk=self.maid_id
        ).update(
            skills_evaluation_method=cleaned_data.get(
                'skills_evaluation_method'
            )
        )
        MaidInfantChildCare.objects.filter(
            maid__pk=self.maid_id
        ).update(
            assessment=cleaned_data.get('cfi_assessment'),
            willingness=cleaned_data.get('cfi_willingness'),
            experience=cleaned_data.get('cfi_experience'),
            remarks=cleaned_data.get('cfi_remarks'),
            other_remarks=cleaned_data.get('cfi_other_remarks')
        )
        MaidElderlyCare.objects.filter(
            maid__pk=self.maid_id
        ).update(
            assessment=cleaned_data.get('cfe_assessment'),
            willingness=cleaned_data.get('cfe_willingness'),
            experience=cleaned_data.get('cfe_experience'),
            remarks=cleaned_data.get('cfe_remarks'),
            other_remarks=cleaned_data.get('cfe_other_remarks')
        )
        MaidDisabledCare.objects.filter(
            maid__pk=self.maid_id
        ).update(
            assessment=cleaned_data.get('cfd_assessment'),
            willingness=cleaned_data.get('cfd_willingness'),
            experience=cleaned_data.get('cfd_experience'),
            remarks=cleaned_data.get('cfd_remarks'),
            other_remarks=cleaned_data.get('cfd_other_remarks')
        )
        MaidGeneralHousework.objects.filter(
            maid__pk=self.maid_id
        ).update(
            assessment=cleaned_data.get('geh_assessment'),
            willingness=cleaned_data.get('geh_willingness'),
            experience=cleaned_data.get('geh_experience'),
            remarks=cleaned_data.get('geh_remarks'),
            other_remarks=cleaned_data.get('geh_other_remarks')
        )
        MaidCooking.objects.filter(
            maid__pk=self.maid_id
        ).update(
            assessment=cleaned_data.get('cok_assessment'),
            willingness=cleaned_data.get('cok_willingness'),
            experience=cleaned_data.get('cok_experience'),
            remarks=cleaned_data.get('cok_remarks'),
            other_remarks=cleaned_data.get('cok_other_remarks')
        )
        MaidOtherCare.objects.filter(
            maid__pk=self.maid_id
        ).update(
            care_for_pets=cleaned_data.get('care_for_pets'),
            gardening=cleaned_data.get('gardening')
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.maid_id
            }
        )

# Redirect Views
class MaidTogglePublished(SpecificAgencyMaidLoginRequiredMixin, RedirectView):
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        try:
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        except Maid.DoesNotExist:
            messages.error(
                self.request,
                'This maid does not exist'
            )
        else:
            maid.published = not maid.published
            maid.save()
            kwargs.pop(self.pk_url_kwarg)
        finally:
            return reverse_lazy(
                'dashboard_maid_list'
            )

class MaidToggleFeatured(SpecificAgencyMaidLoginRequiredMixin, RedirectView):
    pk_url_kwarg = 'pk'

    def get_redirect_url(self, *args, **kwargs):
        try:
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        except Maid.DoesNotExist:
            messages.error(
                self.request,
                'This maid does not exist'
            )
        else:
            if maid.featured == False:
                amt_of_featured = maid.agency.amount_of_featured_biodata
                amt_allowed = maid.agency.amount_of_featured_biodata_allowed
                if amt_of_featured < amt_allowed:
                    maid.featured = not maid.featured
                else:
                    messages.warning(
                        self.request,
                        'You have reached the limit of featured biodata',
                        extra_tags='error'
                    )
            else:
                maid.featured = not maid.featured
            maid.save()
            kwargs.pop(self.pk_url_kwarg)
        finally:
            return reverse_lazy(
                'dashboard_maid_list'
            )
            
# List Views
class MaidList(LoginRequiredMixin, ListFilteredMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    queryset = Maid.objects.filter(published=True)
    template_name = 'list/maid-list.html'
    filter_set = MaidFilter
    paginate_by = settings.MAID_PAGINATE_BY

class MaidEmploymentHistoryList(AgencyLoginRequiredMixin, ListView):
    context_object_name = 'maid_employment_history_list'
    http_method_names = ['get']
    model = MaidEmploymentHistory
    template_name = 'list/maid-employment-history-list.html'

    def get_queryset(self):
        return MaidEmploymentHistory.objects.filter(
            maid__pk = self.kwargs['maid_id'],
            maid__agency = Agency.objects.get(
                pk = self.request.user.pk
            )
        )

# Detail Views
class MaidDetail(LoginRequiredMixin, DetailView):
    context_object_name = 'maid'
    http_method_names = ['get']
    model = Maid
    template_name = 'detail/maid-detail.html'
    
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        country_of_origin = self.object.personal_details.country_of_origin
        languages = self.object.personal_details.languages.all()
        similar_maids = Maid.objects.filter(
            personal_details__country_of_origin=country_of_origin,
            responsibilities=self.object.get_main_responsibility(),
            personal_details__languages__in=languages
        ).exclude(
            pk=self.object.pk
        ).distinct()
        kwargs.update({
            'similar_maids': similar_maids
        })
        return kwargs

# Create Views
class MaidCreate(AgencyLoginRequiredMixin, GetAuthorityMixin, 
                 SuccessMessageMixin, CreateView):
    context_object_name = 'maid'
    form_class = MaidCreationForm
    http_method_names = ['get','post']
    model = Maid
    template_name = 'create/maid-create.html'
    success_url = reverse_lazy('dashboard_maid_detail')
    authority = ''
    agency_id = ''
    success_message = 'FDW Biodata created'

    def form_valid(self, form):
        form.instance.agency = Agency.objects.get(
            pk=self.agency_id
        )
        initial_agency_fee_amount = form.cleaned_data.get(
            'initial_agency_fee_amount'
        )
        initial_agency_fee_description = form.cleaned_data.get(
            'initial_agency_fee_description'
        )
        response = super().form_valid(form)
        MaidPersonalDetails.objects.create(
            maid=self.object
        )
        MaidFamilyDetails.objects.create(
            maid=self.object
        )
        MaidInfantChildCare.objects.create(
            maid=self.object
        )
        MaidElderlyCare.objects.create(
            maid=self.object
        )
        MaidDisabledCare.objects.create(
            maid=self.object
        )
        MaidGeneralHousework.objects.create(
            maid=self.object
        )
        MaidCooking.objects.create(
            maid=self.object
        )
        MaidAgencyFeeTransaction.objects.create(
            maid=self.object,
            amount=initial_agency_fee_amount,
            transaction_type='ADD',
            description=initial_agency_fee_description
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'agency_id': self.agency_id
        })
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk':self.object.pk
            }
        )

class MaidFoodHandlingPreferenceCreate(AgencyLoginRequiredMixin, 
                                       SuccessMessageMixin, CreateView):
    context_object_name = 'maid_food_handling_preference'
    form_class = MaidFoodHandlingPreferenceForm
    http_method_names = ['get','post']
    model = MaidFoodHandlingPreference
    template_name = 'create/maid-food-handling-preference-create.html'
    success_url = reverse_lazy('')
    success_message = 'Maid food handling preference created'

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

class MaidDietaryRestrictionCreate(AgencyLoginRequiredMixin, 
                                   SuccessMessageMixin, CreateView):
    context_object_name = 'maid_dietary_restriction'
    form_class = MaidDietaryRestrictionForm
    http_method_names = ['get','post']
    model = MaidDietaryRestriction
    template_name = 'create/maid-dietary-restriction-create.html'
    success_url = reverse_lazy('')
    success_message = 'Maid dietary restriction created'

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

class MaidEmploymentHistoryCreate(AgencyLoginRequiredMixin,
                                  SuccessMessageMixin, CreateView):
    context_object_name = 'maid_employment_history'
    form_class = MaidEmploymentHistoryForm
    http_method_names = ['get','post']
    model = MaidEmploymentHistory
    template_name = 'create/maid-employment-history-create.html'
    success_url = reverse_lazy('')
    success_message = 'Maid employment history created'

    def form_valid(self, form):
        form.instance.maid = Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            )
        )
        return super().form_valid(form)

# Update Views
class MaidUpdate(SpecificAgencyMaidLoginRequiredMixin, GetAuthorityMixin,
                 SuccessMessageMixin, UpdateView):
    context_object_name = 'maid'
    form_class = MaidUpdateForm
    http_method_names = ['get','post']
    model = Maid
    template_name = 'update/maid-update.html'
    success_message = 'Maid details updated'
    authority = ''
    agency_id = ''

    def get_object(self, queryset=None):
        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency__pk = self.agency_id
        )

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidPersonalDetailsUpdate(SpecificAgencyMaidLoginRequiredMixin, 
                        SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_biodata'
    form_class = MaidPersonalDetailsForm
    http_method_names = ['get','post']
    model = MaidPersonalDetails
    template_name = 'update/maid-biodata-update.html'
    success_message = 'FDW biodata updated'

    def get_object(self, queryset=None):
        return MaidPersonalDetails.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidFamilyDetailsUpdate(SpecificAgencyMaidLoginRequiredMixin, 
                              SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_family_details'
    form_class = MaidFamilyDetailsForm
    http_method_names = ['get','post']
    model = MaidFamilyDetails
    template_name = 'update/maid-family-details-update.html'
    success_message = 'Maid family details updated'

    def get_object(self, queryset=None):
        return MaidFamilyDetails.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidFinancialDetailsUpdate(SpecificAgencyMaidLoginRequiredMixin, 
                              SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_family_details'
    form_class = MaidFinancialDetailsForm
    http_method_names = ['get','post']
    model = MaidFinancialDetails
    template_name = 'update/maid-financial-details-update.html'
    success_message = 'Maid financial details updated'

    def get_object(self, queryset=None):
        return MaidFinancialDetails.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )

    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidInfantChildCareUpdate(
    SpecificAgencyMaidLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_infant_child_care'
    form_class = MaidInfantChildCareForm
    http_method_names = ['get','post']
    model = MaidInfantChildCare
    template_name = 'update/maid-infant-child-care-update.html'
    success_message = 'Maid infant child care information updated'

    def get_object(self, queryset=None):
        return MaidInfantChildCare.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidElderlyCareUpdate(SpecificAgencyMaidLoginRequiredMixin,
                            SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_elderly_care'
    form_class = MaidElderlyCareForm
    http_method_names = ['get','post']
    model = MaidElderlyCare
    template_name = 'update/maid-elderly-care-update.html'
    success_message = 'Maid elderly care information updated'

    def get_object(self, queryset=None):
        return MaidElderlyCare.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidDisabledCareUpdate(SpecificAgencyMaidLoginRequiredMixin,
                             SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_disabled_care'
    form_class = MaidDisabledCareForm
    http_method_names = ['get','post']
    model = MaidDisabledCare
    template_name = 'update/maid-disabled-care-update.html'
    success_message = 'Maid disabled care information updated'

    def get_object(self, queryset=None):
        return MaidDisabledCare.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidGeneralHouseworkUpdate(SpecificAgencyMaidLoginRequiredMixin,
                                 SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_general_housework'
    form_class = MaidGeneralHouseworkForm
    http_method_names = ['get','post']
    model = MaidGeneralHousework
    template_name = 'update/maid-general-housework-update.html'
    success_message = 'Maid general housework care information updated'

    def get_object(self, queryset=None):
        return MaidGeneralHousework.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidCookingUpdate(SpecificAgencyMaidLoginRequiredMixin,
                        SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_cooking'
    form_class = MaidCookingForm
    http_method_names = ['get','post']
    model = MaidCooking
    template_name = 'update/maid-cooking-update.html'
    success_message = 'Maid cooking care information updated'

    def get_object(self, queryset=None):
        return MaidCooking.objects.get(
            maid = Maid.objects.get(
                pk = self.kwargs.get(
                    self.pk_url_kwarg
                )
            )
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk': self.kwargs.get(
                    self.pk_url_kwarg
                )
            }
        )

class MaidEmploymentHistoryUpdate(SpecificAgencyMaidLoginRequiredMixin,
                                  SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_employment_history'
    form_class = MaidEmploymentHistoryForm
    http_method_names = ['get','post']
    model = MaidEmploymentHistory
    template_name = 'update/maid-employment-history-update.html'
    success_url = reverse_lazy('')
    success_message = 'Maid employment history updated'

    def get_object(self, queryset=None):
        return MaidEmploymentHistory.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            maid__agency = self.request.user.agency_owner.agency
        )

class MaidAgencyFeeTransactionUpdate(SpecificAgencyMaidLoginRequiredMixin,
                                  SuccessMessageMixin, UpdateView):
    context_object_name = 'maid_agency_fee_transaction'
    form_class = MaidAgencyFeeTransactionForm
    http_method_names = ['get','post']
    model = MaidAgencyFeeTransaction
    template_name = 'update/maid-agency-fee-transaction-update.html'
    success_message = 'Maid agency fee transaction updated'

    def get_object(self, queryset=None):
        return MaidAgencyFeeTransaction.objects.get(
            pk = self.kwargs.get('agency_fee_transaction_pk'),
            maid = self.kwargs.get('pk'),
            maid__agency = self.request.user.agency_owner.agency
        )
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard_maid_detail',
            kwargs={
                'pk':self.kwargs.get('pk')
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

    def get_object(self, queryset=None):
        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency = self.request.user.agency_owner.agency
        )

class MaidFoodHandlingPreferenceDelete(SpecificAgencyOwnerRequiredMixin,
                                       SuccessMessageMixin, DeleteView):
    context_object_name = 'maid_food_handling_preference'
    http_method_names = ['post']
    model = MaidFoodHandlingPreference
    success_url = reverse_lazy('')
    check_type = 'maid'
    success_message = 'Maid food handling information deleted'

class MaidDietaryRestrictionDelete(SpecificAgencyOwnerRequiredMixin,
                                   SuccessMessageMixin, DeleteView):
    context_object_name = 'maid_dietary_restriction'
    http_method_names = ['post']
    model = MaidDietaryRestriction
    success_url = reverse_lazy('')
    check_type = 'maid'
    success_message = 'Maid dietary restriction deleted'

class MaidEmploymentHistoryDelete(SpecificAgencyOwnerRequiredMixin,
                                  SuccessMessageMixin, DeleteView):
    context_object_name = 'maid_employment_history'
    http_method_names = ['post']
    model = MaidEmploymentHistory
    success_url = reverse_lazy('')
    check_type = 'maid'
    success_message = 'Maid employment history deleted'

    def get_object(self, queryset=None):
        return MaidEmploymentHistory.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            maid__agency = self.request.user.agency_owner.agency
        )

# Generic Views
class MaidProfileView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            selected_maid = Maid.objects.get(
                pk = self.kwargs.get('pk')
            )
        except Maid.DoesNotExist:
            data = {
                'error': 'Maid does not exist'
            }
            return JsonResponse(data, status=404)
        else:
            data = {
                'salary': selected_maid.financial_details.salary,
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
            featured=True
        )
        if nationality != 'ANY':
            featured_maids = featured_maids.filter(
                personal_details__country_of_origin=nationality
            )

        shuffle(list(featured_maids))
        featured_maids = [
            {
                'pk': maid.pk,
                'photo_url': maid.photo.url,
                'name': maid.name,
                'country_of_origin': maid.personal_details.get_country_of_origin_display(),
                'age': maid.personal_details.age,
                'marital_status': maid.family_details.get_marital_status_display(),
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
