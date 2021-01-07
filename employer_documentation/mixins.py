# Python
import base64

# Django
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

# 3rd party
from weasyprint import HTML, CSS

# From our apps
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
    JobOrder,
)
from onlinemaid.constants import (
    AG_OWNERS,
    AG_ADMINS,
    AG_MANAGERS,
    AG_SALES,
)
from accounts.models import User


# Start of mixins
class CheckEmployerDocRelationshipsMixin(UserPassesTestMixin):
    def test_func(self):
        if self.employer_doc_obj:
            if self.object.employer.pk==self.kwargs.get('employer_pk'):
                return True
            else:
                return False
        elif self.employer_subdoc_obj:
            if (
                self.object.employer_doc.employer.pk==self.kwargs.get(
                    'employer_pk')
                and
                self.object.employer_doc.pk==self.kwargs.get(
                    'employerdoc_pk')
            ):
                return True
            else:
                return False
        else:
            return False

class LoginByAgencyUserGroupRequiredMixin(LoginRequiredMixin):
    '''
    This is a helper mixin that does not override any inherited methods or
    attributes. Use to add additional functionality to LoginRequiredMixin.
    '''
    agency_user_group = None
    agency_user_obj = None
    employer_obj = None
    employer_doc_obj = None
    employer_subdoc_obj = None

    # Gets current user's assigned agency group. Needs to be called manually.
    def assign_agency_user_group(self):
        # First check if current user is agency_employee or agency_owner.
        # If neither, then permission check failed, no further checks needed.
        if (
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_employee'
            )
            or
            hasattr(
                User.objects.get(pk=self.request.user.pk), 'agency_owner'
            )
        ):
            # Assign current user's agency group to agency_user_group atribute
            if self.request.user.groups.filter(name=AG_OWNERS).exists():
                self.agency_user_group = AG_OWNERS
            elif (
                self.request.user.groups.filter(name=AG_ADMINS)
                .exists()
            ):
                self.agency_user_group = AG_ADMINS
            elif (
                self.request.user.groups.filter(name=AG_MANAGERS).exists()
            ):
                self.agency_user_group = AG_MANAGERS
            elif (
                self.request.user.groups.filter(name=AG_SALES)
                .exists()
            ):
                self.agency_user_group = AG_SALES
            else:
                return self.handle_no_permission()
            # If successfully assigned current user's agency group to
            # agency_user_group atribute, return True so this method can also
            # serve as a validation that current user has agency role.
            return True
            
        else:
            return self.handle_no_permission()

    # Gets current user's object. Call assign_agency_user_group() first to set
    # agency_user_group attribute
    def assign_agency_user_object(self):
        if self.agency_user_group==AG_OWNERS:
            self.agency_user_obj = self.request.user.agency_owner
        else:
            self.agency_user_obj = self.request.user.agency_employee

    # Method to get object Employer, EmployerDoc, EmployerDocMaidStatus,
    # EmployerDocSig from database and assign to attribute of View object.
    def assign_ed_object(self):
        # Try to get object from database
        try:
            if not hasattr(self, 'object'): self.object = self.get_object()
        except:
            return self.handle_no_permission()
        else:
            # Assign to respective attribute
            if isinstance(self.object, Employer):
                self.employer_obj = self.object
            elif isinstance(self.object, EmployerDoc):
                self.employer_doc_obj = self.object
            elif (
                isinstance(self.object, EmployerDocMaidStatus)
                or isinstance(self.object, EmployerDocSig)
                or isinstance(self.object, JobOrder)
            ):
                self.employer_subdoc_obj = self.object

    # Method to check object's agency is same as current user's agency
    def check_object_belongs_to_agency(self):
        if (
            self.employer_obj and
            not self.employer_obj.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()
        elif (
            self.employer_doc_obj and
            not self.employer_doc_obj.employer.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()
        elif (
            self.employer_subdoc_obj and
            not self.employer_subdoc_obj.employer_doc.employer
            .agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()
        return super().dispatch(request, *args, **kwargs)

class CheckAgencyEmployeePermissionsMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()

        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_ed_object()

        # Check test object's agency is same as current user's agency
        self.check_object_belongs_to_agency()

        # Check user belongs to required group to access view
        if (
            self.agency_user_group==AG_OWNERS
            or
            self.agency_user_group==AG_ADMINS
            or (
                self.agency_user_group==AG_MANAGERS and
                self.employer_obj and
                self.agency_user_obj.branch==
                self.employer_obj.agency_employee.branch
            )
            or (
                self.agency_user_group==AG_MANAGERS and
                self.employer_doc_obj and
                self.agency_user_obj.branch==
                self.employer_doc_obj.employer.agency_employee.branch
            )
            or (
                self.agency_user_group==AG_MANAGERS and
                self.employer_subdoc_obj and
                self.agency_user_obj.branch==
                self.employer_subdoc_obj.employer_doc.employer.agency_employee
                .branch
            )
            or (
                self.employer_obj and
                self.employer_obj.agency_employee==self.agency_user_obj
            )
            or (
                self.employer_doc_obj and
                self.employer_doc_obj.employer.agency_employee
                ==self.agency_user_obj
            )
            or (
                self.employer_subdoc_obj and
                self.employer_subdoc_obj.employer_doc.employer.agency_employee
                ==self.agency_user_obj
            )
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckUserIsAgencyOwnerMixin(LoginByAgencyUserGroupRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Get current user's agency_user_group and agency_user_obj
        if not self.agency_user_group:  self.assign_agency_user_group()
        if not self.agency_user_obj:    self.assign_agency_user_object()
        
        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_ed_object()
        
        # Check test object's agency is same as current user's agency
        self.check_object_belongs_to_agency()

        # Check if current user is agency owner
        if self.agency_user_group==AG_OWNERS:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

# Signature Mixin
class CheckSignatureSessionTokenMixin(UserPassesTestMixin):
    def test_func(self):
        if (
            self.request.session.get('signature_token') ==
            getattr(self.get_object(), self.token_field_name)
        ):
            return True
        else:
            return False

# PDF Mixin
class PdfHtmlViewMixin:
    DEFAULT_DOWNLOAD_FILENAME = "document.pdf"
    content_disposition = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.rn_maidstatus_ed.fdw_work_commencement_date:
            return HttpResponseRedirect(
                reverse('employerdoc_status_update_route', kwargs={
                    'employer_pk': self.object.employer.pk,
                    'employerdoc_pk': self.object.pk,
                    'employersubdoc_pk': self.object.rn_maidstatus_ed.pk,
                }))

        context = self.get_context_data(object=self.object)

        # Render PDF
        html_template = render_to_string(self.template_name, context)
        pdf_file = HTML(
            string=html_template,
            base_url=request.build_absolute_uri()
            ).write_pdf(
                # Load separate CSS stylesheet from static folder
                # stylesheets=[CSS(settings.STATIC_ROOT + 'css/styles.css')]
                stylesheets=[CSS('static/css/pdf.css'
                )]
            )
        response = HttpResponse(pdf_file, content_type='application/pdf')
        if self.content_disposition:
            response['Content-Disposition'] = self.content_disposition
        else:
            response['Content-Disposition'] = (
                'inline; filename=' + self.DEFAULT_DOWNLOAD_FILENAME
            )
        return response
