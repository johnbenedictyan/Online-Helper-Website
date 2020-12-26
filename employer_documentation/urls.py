# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## List Views
from .views import (
    EmployerListView,
    EmployerDocListView,
)

# ## Detail Views
from .views import (
    EmployerDetailView,
    EmployerDocDetailView,
)

## Create Views
from .views import (
    EmployerCreateView,
    EmployerDocCreateView,
)

## Update Views
from .views import (
    EmployerUpdateView,
#     EmployerBaseUpdateAgentView,
#     EmployerExtraInfoUpdateView,
#     EmployerDocBaseUpdateView,
#     EmployerDocJobOrderUpdateView,
#     EmployerDocServiceFeeBaseUpdateView,
#     EmployerDocServiceAgreementUpdateView,
#     EmployerDocEmploymentContractUpdateView,
)

# ## Delete Views
from .views import (
    EmployerDeleteView,
    # EmployerDocDeleteView,
)

# ## Signature Views
# from .views import (
#     SignatureEmployerCreateView,
#     SignatureEmployerUpdateView,
#     SignatureSpouseCreateView,
#     SignatureSpouseUpdateView,
#     SignatureSponsorCreateView,
#     SignatureSponsorUpdateView,
#     SignatureFdwCreateView,
#     SignatureFdwUpdateView,
#     SignatureAgencyStaffCreateView,
#     SignatureAgencyStaffUpdateView,
# )

# ## PDF Views
# from .views import (
#     PdfEmployerAgreementView,
#     PdfRepaymentScheduleView,
# )

# Start of Urls
urlpatterns = [
    path(
        '',
        include([
            path(
                'create/',
                EmployerCreateView.as_view(),
                name='employer_create_route'
            ),
            path(
                'employer-list/',
                EmployerListView.as_view(),
                name='employer_list_route'
            ),
            path(
                '<uuid:employer_pk>/',
                include([
                    path(
                        'detail/',
                        EmployerDetailView.as_view(),
                        name='employer_detail_route'
                    ),
                    path(
                        'update/',
                        EmployerUpdateView.as_view(),
                        name='employer_update_route'
                    ),
                    path(
                        'delete/',
                        EmployerDeleteView.as_view(),
                        name='employer_delete_route'
                    ),
                    path(
                        'documentation/',
                        include([
                            path(
                                'create/',
                                EmployerDocCreateView.as_view(),
                                name='employerdoc_create_route'
                            ),
                            path(
                                'list/',
                                EmployerDocListView.as_view(),
                                name='employerdoc_list_route'
                            ),
                        path(
                            '<uuid:employerdoc_pk>/',
                            include([
                                path(
                                    'detail/',
                                    EmployerDocDetailView.as_view(),
                                    name='employerdoc_detail_route'
                                ),
                            ]),
                        ),
                        ]),
                    ),
                ]),
            ),
        ]),
    ),
]

# urlpatterns = [
#     path(
#         '',
#         include([
#             path(
#                 '<uuid:employer_base_pk>/',
#                 include([
#                     path(
#                         'update-agent/',
#                         EmployerBaseUpdateAgentView.as_view(),
#                         name='employer_base_agent_update'
#                     ),
#                     path(
#                         'doc-base/<int:employerdoc_base_pk>/',
#                         include([
#                             path(
#                                 'detail/',
#                                 EmployerDocBaseDetailView.as_view(),
#                                 name='employerdoc_base_detail'
#                             ),
#                             path(
#                                 'update/',
#                                 EmployerDocBaseUpdateView.as_view(),
#                                 name='employerdoc_base_update'
#                             ),
#                             path(
#                                 'delete/',
#                                 EmployerDocBaseDeleteView.as_view(),
#                                 name='employerdoc_base_delete'
#                             ),
#                             path(
#                                 'job-order/create/',
#                                 EmployerDocJobOrderCreateView.as_view(),
#                                 name='employerdoc_job_order_create'
#                             ),
#                             path(
#                                 'job-order/<int:employerdoc_job_order_pk>/update/',
#                                 EmployerDocJobOrderUpdateView.as_view(),
#                                 name='employerdoc_job_order_update'
#                             ),
#                             path(
#                                 'service-fee/create/',
#                                 EmployerDocServiceFeeBaseCreateView.as_view(),
#                                 name='employerdoc_service_fee_base_create'
#                             ),
#                             path(
#                                 'service-fee/<int:employerdoc_service_fee_base_pk>/update/',
#                                 EmployerDocServiceFeeBaseUpdateView.as_view(),
#                                 name='employerdoc_service_fee_base_update'
#                             ),
#                             path(
#                                 'service-agreement/create/',
#                                 EmployerDocServiceAgreementCreateView.as_view(),
#                                 name='employerdoc_service_agreement_create'
#                             ),
#                             path(
#                                 'service-agreement/<int:employerdoc_service_agreement_pk>/update/',
#                                 EmployerDocServiceAgreementUpdateView.as_view(),
#                                 name='employerdoc_service_agreement_update'
#                             ),
#                             path(
#                                 'employment-contract/create/',
#                                 EmployerDocEmploymentContractCreateView.as_view(),
#                                 name='employerdoc_employment_contract_create'
#                             ),
#                             path(
#                                 'employment-contract/<int:employerdoc_employment_contract_pk>/update/',
#                                 EmployerDocEmploymentContractUpdateView.as_view(),
#                                 name='employerdoc_employment_contract_update'
#                             ),
#                             path(
#                                 'signature/employer/create/',
#                                 SignatureEmployerCreateView.as_view(),
#                                 name='signature_employer_create'
#                             ),
#                             path(
#                                 'signature/<int:docsig_pk>/employer/update/',
#                                 SignatureEmployerUpdateView.as_view(),
#                                 name='signature_employer_update'
#                             ),
#                             path(
#                                 'signature/spouse/create/',
#                                 SignatureSpouseCreateView.as_view(),
#                                 name='signature_spouse_create'
#                             ),
#                             path(
#                                 'signature/<int:docsig_pk>/spouse/update/',
#                                 SignatureSpouseUpdateView.as_view(),
#                                 name='signature_spouse_update'
#                             ),
#                             path(
#                                 'signature/sponsor/create/',
#                                 SignatureSponsorCreateView.as_view(),
#                                 name='signature_sponsor_create'
#                             ),
#                             path(
#                                 'signature/<int:docsig_pk>/sponsor/update/',
#                                 SignatureSponsorUpdateView.as_view(),
#                                 name='signature_sponsor_update'
#                             ),
#                             path(
#                                 'signature/fdw/create/',
#                                 SignatureFdwCreateView.as_view(),
#                                 name='signature_fdw_create'
#                             ),
#                             path(
#                                 'signature/<int:docsig_pk>/fdw/update/',
#                                 SignatureFdwUpdateView.as_view(),
#                                 name='signature_fdw_update'
#                             ),
#                             path(
#                                 'signature/agency/create/',
#                                 SignatureAgencyStaffCreateView.as_view(),
#                                 name='signature_agency_create'
#                             ),
#                             path(
#                                 'signature/<int:docsig_pk>/agency/update/',
#                                 SignatureAgencyStaffUpdateView.as_view(),
#                                 name='signature_agency_update'
#                             ),
#                             path(
#                                 'pdf/service-fees/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-01-service-fee-base.html',
#                                     content_disposition = 'inline; filename="service_fee_schedule.pdf"',
#                                 ),
#                                 name='pdf_service_fee_base'
#                             ),
#                             path(
#                                 'pdf/service-agreement/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-03-service-agreement.html',
#                                     content_disposition = 'inline; filename="service_agreement.pdf"',
#                                 ),
#                                 name='pdf_service_agreement'
#                             ),
#                             path(
#                                 'pdf/employment-contract/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-04-employment-contract.html',
#                                     content_disposition = 'inline; filename="employment-contract.pdf"',
#                                 ),
#                                 name='pdf_employment_contract'
#                             ),
#                             path(
#                                 'pdf/repayment-schedule/',
#                                 PdfRepaymentScheduleView.as_view(
#                                     template_name='employer_documentation/pdf-05-repayment-schedule.html',
#                                     content_disposition = 'inline; filename="repayment-schedule.pdf"',
#                                 ),
#                                 name='pdf_repayment_schedule'
#                             ),
#                             path(
#                                 'pdf/rest-day-agreement/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-06-rest-day-agreement.html',
#                                     content_disposition = 'inline; filename="rest-day-agreement.pdf"',
#                                 ),
#                                 name='pdf_rest_day_agreement'
#                             ),
#                             path(
#                                 'pdf/job-order/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-07-job-order.html',
#                                     content_disposition = 'inline; filename="job-order.pdf"',
#                                 ),
#                                 name='pdf_job_order'
#                             ),
#                             path(
#                                 'pdf/handover-checklist/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-08-handover-checklist.html',
#                                     content_disposition = 'inline; filename="handover-checklist.pdf"',
#                                 ),
#                                 name='pdf_handover_checklist'
#                             ),
#                             path(
#                                 'pdf/transfer-consent/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-09-transfer-consent.html',
#                                     content_disposition = 'inline; filename="transfer-consent.pdf"',
#                                 ),
#                                 name='pdf_transfer_consent'
#                             ),
#                             path(
#                                 'pdf/work-pass-authorisation/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-10-work-pass-authorisation.html',
#                                     content_disposition = 'inline; filename="work-pass-authorisation.pdf"',
#                                 ),
#                                 name='pdf_work_pass_authorisation'
#                             ),
#                             path(
#                                 'pdf/security-bond/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-11-security-bond.html',
#                                     content_disposition = 'inline; filename="security-bond.pdf"',
#                                 ),
#                                 name='pdf_security_bond'
#                             ),
#                             path(
#                                 'pdf/fdw-work-permit-12b/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-12-fdw-work-permit.html',
#                                     content_disposition = 'inline; filename="fdw-work-permit-form-12b.pdf"',
#                                 ),
#                                 name='pdf_fdw_work_permit_12b'
#                             ),
#                             path(
#                                 'pdf/income-tax-declaration/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-13-income-tax-declaration.html',
#                                     content_disposition = 'inline; filename="income-tax-declaration.pdf"',
#                                 ),
#                                 name='pdf_income_tax_declaration'
#                             ),
#                             path(
#                                 'pdf/safety-agreement/',
#                                 PdfEmployerAgreementView.as_view(
#                                     template_name='employer_documentation/pdf-14-safety-agreement.html',
#                                     content_disposition = 'inline; filename="safety-agreement.pdf"',
#                                 ),
#                                 name='pdf_safety_agreement'
#                             ),
#                         ]),
#                     ),
#                 ]),
#             ),
#         ]),
#     ),
# ]
