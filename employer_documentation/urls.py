# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## List Views
from .views import (
    EmployerBaseListView,
    EmployerDocBaseListView,
)

## Detail Views
from .views import (
    EmployerBaseDetailView,
    EmployerDocBaseDetailView,
)

## Create Views
from .views import (
    EmployerBaseCreateView,
    EmployerExtraInfoCreateView,
    EmployerDocBaseCreateView,
    EmployerDocJobOrderCreateView,
    EmployerDocServiceFeeBaseCreateView,
    EmployerDocServiceAgreementCreateView,
    EmployerDocEmploymentContractCreateView,
)

## Update Views
from .views import (
    EmployerBaseUpdateView,
    EmployerBaseUpdateAgentView,
    EmployerExtraInfoUpdateView,
    EmployerDocBaseUpdateView,
    EmployerDocJobOrderUpdateView,
    EmployerDocServiceFeeBaseUpdateView,
    EmployerDocServiceAgreementUpdateView,
    EmployerDocEmploymentContractUpdateView,
)

## Delete Views
from .views import (
    EmployerBaseDeleteView,
    EmployerDocBaseDeleteView,
)

## Signature Views
from .views import (
    SignatureEmployerCreateView,
    SignatureEmployerUpdateView,
    SignatureSpouseCreateView,
    SignatureSpouseUpdateView,
    SignatureSponsorCreateView,
    SignatureSponsorUpdateView,
    SignatureFdwCreateView,
    SignatureFdwUpdateView,
    SignatureAgencyStaffCreateView,
    SignatureAgencyStaffUpdateView,
)

## PDF Views
from .views import (
    PdfEmployerAgreementView,
)

# Start of Urls
urlpatterns = [
    path(
        '',
        include([
            path(
                'create/',
                EmployerBaseCreateView.as_view(),
                name='employer_base_create'
            ),
            path(
                'employers-list/',
                EmployerBaseListView.as_view(),
                name='employer_base_list'
            ),
            path(
                '<uuid:employer_base_pk>/',
                include([
                    path(
                        'detail/',
                        EmployerBaseDetailView.as_view(),
                        name='employer_base_detail'
                    ),
                    path(
                        'update/',
                        EmployerBaseUpdateView.as_view(),
                        name='employer_base_update'
                    ),
                    path(
                        'update-agent/',
                        EmployerBaseUpdateAgentView.as_view(),
                        name='employer_base_agent_update'
                    ),
                    path(
                        'delete/',
                        EmployerBaseDeleteView.as_view(),
                        name='employer_base_delete'
                    ),
                    path(
                        'extra-info/create/',
                        EmployerExtraInfoCreateView.as_view(),
                        name='employer_extra_info_create'
                    ),
                    path(
                        'extra-info/<int:employer_extra_info_pk>/update/',
                        EmployerExtraInfoUpdateView.as_view(),
                        name='employer_extra_info_update'
                    ),
                    path(
                        'doc-base/create/',
                        EmployerDocBaseCreateView.as_view(),
                        name='employer_doc_base_create'
                    ),
                    path(
                        'doc-base/list/',
                        EmployerDocBaseListView.as_view(),
                        name='employer_doc_base_list'
                    ),
                    path(
                        'doc-base/<int:employer_doc_base_pk>/',
                        include([
                            path(
                                'detail/',
                                EmployerDocBaseDetailView.as_view(),
                                name='employer_doc_base_detail'
                            ),
                            path(
                                'update/',
                                EmployerDocBaseUpdateView.as_view(),
                                name='employer_doc_base_update'
                            ),
                            path(
                                'delete/',
                                EmployerDocBaseDeleteView.as_view(),
                                name='employer_doc_base_delete'
                            ),
                            path(
                                'job-order/create/',
                                EmployerDocJobOrderCreateView.as_view(),
                                name='employer_doc_job_order_create'
                            ),
                            path(
                                'job-order/<int:employer_doc_job_order_pk>/update/',
                                EmployerDocJobOrderUpdateView.as_view(),
                                name='employer_doc_job_order_update'
                            ),
                            path(
                                'service-fee/create/',
                                EmployerDocServiceFeeBaseCreateView.as_view(),
                                name='employer_doc_service_fee_base_create'
                            ),
                            path(
                                'service-fee/<int:employer_doc_service_fee_base_pk>/update/',
                                EmployerDocServiceFeeBaseUpdateView.as_view(),
                                name='employer_doc_service_fee_base_update'
                            ),
                            path(
                                'service-agreement/create/',
                                EmployerDocServiceAgreementCreateView.as_view(),
                                name='employer_doc_service_agreement_create'
                            ),
                            path(
                                'service-agreement/<int:employer_doc_service_agreement_pk>/update/',
                                EmployerDocServiceAgreementUpdateView.as_view(),
                                name='employer_doc_service_agreement_update'
                            ),
                            path(
                                'employment-contract/create/',
                                EmployerDocEmploymentContractCreateView.as_view(),
                                name='employer_doc_employment_contract_create'
                            ),
                            path(
                                'employment-contract/<int:employer_doc_employment_contract_pk>/update/',
                                EmployerDocEmploymentContractUpdateView.as_view(),
                                name='employer_doc_employment_contract_update'
                            ),
                            path(
                                'signature/employer/create/',
                                SignatureEmployerCreateView.as_view(),
                                name='signature_employer_create'
                            ),
                            path(
                                'signature/<int:docsig_pk>/employer/update/',
                                SignatureEmployerUpdateView.as_view(),
                                name='signature_employer_update'
                            ),
                            path(
                                'signature/spouse/create/',
                                SignatureSpouseCreateView.as_view(),
                                name='signature_spouse_create'
                            ),
                            path(
                                'signature/<int:docsig_pk>/spouse/update/',
                                SignatureSpouseUpdateView.as_view(),
                                name='signature_spouse_update'
                            ),
                            path(
                                'signature/sponsor/create/',
                                SignatureSponsorCreateView.as_view(),
                                name='signature_sponsor_create'
                            ),
                            path(
                                'signature/<int:docsig_pk>/sponsor/update/',
                                SignatureSponsorUpdateView.as_view(),
                                name='signature_sponsor_update'
                            ),
                            path(
                                'signature/fdw/create/',
                                SignatureFdwCreateView.as_view(),
                                name='signature_fdw_create'
                            ),
                            path(
                                'signature/<int:docsig_pk>/fdw/update/',
                                SignatureFdwUpdateView.as_view(),
                                name='signature_fdw_update'
                            ),
                            path(
                                'signature/agency/create/',
                                SignatureAgencyStaffCreateView.as_view(),
                                name='signature_agency_create'
                            ),
                            path(
                                'signature/<int:docsig_pk>/agency/update/',
                                SignatureAgencyStaffUpdateView.as_view(),
                                name='signature_agency_update'
                            ),
                            path(
                                'pdf/service-fees/',
                                PdfEmployerAgreementView.as_view(
                                    template_name='employer_documentation/pdf-01-service-fee-base.html',
                                    content_disposition = 'inline; filename="service_fee_schedule.pdf"',
                                ),
                                name='pdf_service_fee_base'
                            ),
                            path(
                                'pdf/service-agreement/',
                                PdfEmployerAgreementView.as_view(
                                    template_name='employer_documentation/pdf-03-service-agreement.html',
                                    content_disposition = 'inline; filename="service_agreement.pdf"',
                                ),
                                name='pdf_service_agreement'
                            ),
                            path(
                                'pdf/employment-contract/',
                                PdfEmployerAgreementView.as_view(
                                    template_name='employer_documentation/pdf-04-employment-contract.html',
                                    content_disposition = 'inline; filename="employment-contract.pdf"',
                                ),
                                name='pdf_employment_contract'
                            ),
                            path(
                                'pdf/repayment-schedule/',
                                PdfEmployerAgreementView.as_view(
                                    template_name='employer_documentation/pdf-05-repayment-schedule.html',
                                    content_disposition = 'inline; filename="repayment-schedule.pdf"',
                                ),
                                name='pdf_repayment_schedule'
                            ),
                        ]),
                    ),
                ]),
            ),
        ]),
    ),
]
