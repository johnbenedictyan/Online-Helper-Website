# Django
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

# From our apps
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
)
from accounts.models import User
# from agency.models import (
#     AgencyEmployee,
#     AgencyOwner,
# )

# Constants: agency user groups
AG_OWNERS = 'Agency Owners'
AG_ADMINS = 'Agency Administrators'
AG_MANAGERS = 'Agency Managers'
AG_SALES = 'Agency Sales Staff'

# Start of mixins
# class CheckEmployerExtraInfoBelongsToEmployerMixin(UserPassesTestMixin):
#     def test_func(self):
#         test_obj = EmployerExtraInfo.objects.get(
#             pk=self.kwargs.get('employer_extra_info_pk')
#         )
#         if test_obj.employer_base.pk==self.kwargs.get('employer_base_pk'):
#             return True
#         else:
#             return False

# class CheckEmployerDocBaseBelongsToEmployerMixin(UserPassesTestMixin):
#     def test_func(self):
#         test_obj = EmployerDocBase.objects.get(
#             pk=self.kwargs.get('employer_doc_base_pk')
#         )
#         if test_obj.employer.pk==self.kwargs.get('employer_base_pk'):
#             return True
#         else:
#             return False

# class CheckEmployerSubDocBelongsToEmployerMixin(UserPassesTestMixin):
#     def test_func(self):
#         # Access employer_doc_base object via current view's object
#         test_obj = self.get_object().employer_doc_base
#         if (
#             test_obj.employer.pk==self.kwargs.get('employer_base_pk')
#             and
#             test_obj.pk==self.kwargs.get('employer_doc_base_pk')
#         ):
#             return True
#         else:
#             return False

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
    def get_agency_user_group(self):
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

    # Gets current user's object. Call get_agency_user_group() first to set
    # agency_user_group attribute
    def get_agency_user_object(self):
        if self.agency_user_group==AG_OWNERS:
            self.agency_user_obj = self.request.user.agency_owner
        else:
            self.agency_user_obj = self.request.user.agency_employee

    # Method to get object Employer, EmployerDoc, EmployerDocMaidStatus,
    # EmployerDocSig from database and assign to attribute of View object.
    def assign_object(self):
        # Try to get object from database
        try:
            self.object = self.get_object()
        except:
            pass
        else:
            # Assign to respective attribute
            if isinstance(self.object, Employer):
                self.employer_obj = self.object
            elif isinstance(self.object, EmployerDoc):
                self.employer_doc_obj = self.object
            elif (
                isinstance(self.object, EmployerDocMaidStatus)
                or isinstance(self.object, EmployerDocSig)
            ):
                self.employer_subdoc_obj = self.object

class CheckAgencyEmployeePermissionsMixin(
    LoginByAgencyUserGroupRequiredMixin
):
    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Get current user's group and user object
        self.get_agency_user_group()
        self.get_agency_user_object()

        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_object()

        # Check test object's agency is same as current user's agency
        if (
            self.employer_obj and
            not self.employer_obj.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()
        elif (
            self.employer_doc_obj and
            not self.employer_doc_obj.rn_ed_employer.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()

        # Check user belongs to required group to access view
        if (
            self.agency_user_group==AG_OWNERS
            or
            self.agency_user_group==AG_ADMINS
            or (
                self.agency_user_group==AG_MANAGERS
                and
                self.agency_user_obj.branch
                == self.employer_obj.agency_employee.branch
            )
            or
            self.employer_obj.agency_employee==self.agency_user_obj
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

class CheckUserIsAgencyOwnerMixin(LoginByAgencyUserGroupRequiredMixin):
    employer_obj = None
    employer_doc_obj = None

    def dispatch(self, request, *args, **kwargs):
        # First check if current user is logged in, if not immediately return
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Get current user's group
        self.get_agency_user_group()
        self.get_agency_user_object()
        
        # Assign Employer, EmployerDoc, EmployerMaidStatus, EmployerDocSig
        # object, if it exists, to attribute of View object.
        self.assign_object()
        
        # Check test object's agency is same as current user's agency
        if (
            self.employer_obj and
            not self.employer_obj.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()
        elif (
            self.employer_doc_obj and
            not self.employer_doc_obj.rn_ed_employer.agency_employee.agency
            ==self.agency_user_obj.agency
        ):
            return self.handle_no_permission()

        # Check if current user is agency owner
        if self.agency_user_group==AG_OWNERS:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

# class CheckAgencyEmployeePermissionsDocBaseMixin(
#     LoginByAgencyUserGroupRequiredMixin
# ):
#     login_url = reverse_lazy('agency_sign_in')
#     permission_denied_message = '''You do not have the necessary access
#                                 rights to perform this action'''

#     def dispatch(self, request, *args, **kwargs):
#         # First check if current user is logged in, if not immediately return
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
        
#         # Get current user's group and user object
#         self.get_agency_user_group()
#         self.get_agency_user_object()
        
#         test_obj = EmployerDocBase.objects.get(
#             pk=self.kwargs.get('employer_doc_base_pk')
#         )

#         # Check test object's agency is same as current user's agency
#         if not test_obj.employer.agency_employee.agency==self.agency_user_obj.agency:
#             return self.handle_no_permission()

#         # Check user belongs to required group to access view
#         if (
#             request.user.groups.filter(name=AG_OWNERS).exists()
#             or
#             request.user.groups.filter(name=AG_ADMINS).exists()
#             or (
#                 request.user.groups.filter(name=AG_MANAGERS).exists()
#                 and
#                 test_obj.employer.agency_employee.branch==self.agency_user_obj.branch
#             )
#             or
#             test_obj.employer.agency_employee==self.agency_user_obj
#         ):
#             return super().dispatch(request, *args, **kwargs)
#         else:
#             return self.handle_no_permission()

# class CheckAgencyEmployeePermissionsSubDocMixin(
#     LoginByAgencyUserGroupRequiredMixin
# ):
#     login_url = reverse_lazy('agency_sign_in')
#     permission_denied_message = '''You do not have the necessary access
#                                 rights to perform this action'''

#     def dispatch(self, request, *args, **kwargs):
#         # First check if current user is logged in, if not immediately return
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
        
#         # Get current user's group and user object
#         self.get_agency_user_group()
#         self.get_agency_user_object()
        
#         # Check test object's agency is same as current user's agency
#         if (
#             not self.get_object().employer_doc_base.employer.agency_employee
#             .agency==self.agency_user_obj.agency
#         ):
#             return self.handle_no_permission()

#         # Check user belongs to required group to access view
#         if (
#             request.user.groups.filter(name=AG_OWNERS).exists()
#             or
#             request.user.groups.filter(name=AG_ADMINS).exists()
#             or (
#                 request.user.groups.filter(name=AG_MANAGERS).exists()
#                 and
#                 self.get_object().employer_doc_base.employer.agency_employee
#                 .branch==self.agency_user_obj.branch
#             )
#             or
#             self.get_object().employer_doc_base.employer.agency_employee
#             ==self.agency_user_obj
#         ):
#             return super().dispatch(request, *args, **kwargs)
#         else:
#             return self.handle_no_permission()

# # Signature Mixin
# import base64
# class SignatureFormMixin:
#     model_field_name = 'signature'

#     def clean(self):
#         cleaned_data = super().clean()
#         base64_sig = cleaned_data.get(self.model_field_name)
#         if base64_sig==None:
#             error_msg = "There was an issue uploading your signature. \
#                 Please try again."
#             self.add_error(self.model_field_name, error_msg)
#         elif not base64_sig.startswith("data:image/png;base64,"):
#             error_msg = "There was an issue uploading your signature. \
#                 Please try again."
#             self.add_error(self.model_field_name, error_msg)
#         elif base64_sig == 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASw\
#             AAACWCAYAAABkW7XSAAAAxUlEQVR4nO3BMQEAAADCoPVPbQhfoAAAAAAAAAAAAAAA\
#                 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
#                     AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
#                         AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
#                             AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOA1\
#                                 v9QAATX68/0AAAAASUVORK5CYII=':
#             error_msg = "Signature cannot be blank."
#             self.add_error(self.model_field_name, error_msg)
#         else:
#             return cleaned_data

# # PDF Mixin
# from django.conf import settings
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from weasyprint import HTML, CSS
# class PdfViewMixin:
#     DEFAULT_DOWNLOAD_FILENAME = "document.pdf"
#     content_disposition = None

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data(object=self.object)

#         # Render PDF
#         html_template = render_to_string(self.template_name, context)
#         pdf_file = HTML(
#             string=html_template,
#             base_url=request.build_absolute_uri()
#             ).write_pdf(
#                 # Load separate CSS stylesheet from static folder
#                 # stylesheets=[CSS(settings.STATIC_ROOT + 'css/styles.css')]
#                 stylesheets=[CSS('static/css/pdf.css'
#                 )]
#             )
#         response = HttpResponse(pdf_file, content_type='application/pdf')
#         if self.content_disposition:
#             response['Content-Disposition'] = self.content_disposition
#         else:
#             response['Content-Disposition'] = (
#                 'inline; filename=' + self.DEFAULT_DOWNLOAD_FILENAME
#             )
#         return response
