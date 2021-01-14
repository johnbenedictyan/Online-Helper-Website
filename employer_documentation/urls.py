# Imports from django
from django.urls import include, path

## List Views
from .views import (
    EmployerListView,
    EmployerDocListView,
)

## Detail Views
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
    EmployerDocUpdateView,
    EmployerDocAgreementDateUpdateView,
    EmployerDocMaidStatusUpdateView,
    JobOrderUpdateView,
)

## Delete Views
from .views import (
    EmployerDeleteView,
    EmployerDocDeleteView,
)

## Signature Views
from .views import (
    SignatureUpdateByAgentView,
    VerifyUserTokenView,
    SignatureUpdateByTokenView,
)

## PDF Views
from .views import (
    PdfGenericAgencyView,
    PdfServiceAgreementAgencyView,
    PdfRepaymentScheduleAgencyView,
    PdfFileAgencyView,
    PdfGenericTokenView,
    PdfServiceAgreementTokenView,
    PdfRepaymentScheduleTokenView,
    PdfFileTokenView,
)

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
                                    path(
                                        'update/',
                                        EmployerDocUpdateView.as_view(),
                                        name='employerdoc_update_route'
                                    ),
                                    path(
                                        'delete/',
                                        EmployerDocDeleteView.as_view(),
                                        name='employerdoc_delete_route'
                                    ),
                                    path(
                                        'agreement-date/<int:employersubdoc_pk>/update/',
                                        EmployerDocAgreementDateUpdateView.as_view(),
                                        name='employerdoc_agreement_date_update_route'
                                    ),
                                    path(
                                        'status/<int:employersubdoc_pk>/update/',
                                        EmployerDocMaidStatusUpdateView.as_view(),
                                        name='employerdoc_status_update_route'
                                    ),
                                    path(
                                        'job-order/<int:employersubdoc_pk>/update/',
                                        JobOrderUpdateView.as_view(),
                                        name='joborder_update_route'
                                    ),
                                    path(
                                        'signature/<int:docsig_pk>/',
                                        include([
                                            path(
                                                'agent-access/employer/update/',
                                                SignatureUpdateByAgentView.as_view(
                                                    model_field_name='employer_signature',
                                                    form_fields=['employer_signature'],
                                                ),
                                                name='signature_employer_update_route'
                                            ),
                                            path(
                                                'agent-access/spouse/update/',
                                                SignatureUpdateByAgentView.as_view(
                                                    model_field_name='spouse_signature',
                                                    form_fields=['employer_signature'],
                                                ),
                                                name='signature_spouse_update_route'
                                            ),
                                            path(
                                                'agent-access/sponsor/update/',
                                                SignatureUpdateByAgentView.as_view(
                                                    model_field_name='sponsor_signature',
                                                    form_fields=['employer_signature'],
                                                ),
                                                name='signature_sponsor_update_route'
                                            ),
                                            path(
                                                'agent-access/fdw/update/',
                                                SignatureUpdateByAgentView.as_view(
                                                    model_field_name='fdw_signature',
                                                    form_fields=['employer_signature'],
                                                ),
                                                name='signature_fdw_update_route'
                                            ),
                                            path(
                                                'agent-access/agency-staff/update/',
                                                SignatureUpdateByAgentView.as_view(
                                                    model_field_name='agency_staff_signature',
                                                    form_fields=['employer_signature'],
                                                ),
                                                name='signature_agency_staff_update_route'
                                            ),
                                        ]),
                                    ),
                                    path(
                                        'pdf/service-fees/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-01-service-fee-schedule.html',
                                            content_disposition = 'inline; filename="service_fee_schedule.pdf"',
                                        ),
                                        name='pdf_agency_service_fee_schedule'
                                    ),
                                    path(
                                        'pdf/service-agreement/',
                                        PdfServiceAgreementAgencyView.as_view(
                                            template_name='employer_documentation/pdf-03-service-agreement.html',
                                            content_disposition = 'inline; filename="service_agreement.pdf"',
                                        ),
                                        name='pdf_agency_service_agreement'
                                    ),
                                    path(
                                        'pdf/employment-contract/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-04-employment-contract.html',
                                            content_disposition = 'inline; filename="employment-contract.pdf"',
                                        ),
                                        name='pdf_agency_employment_contract'
                                    ),
                                    path(
                                        'pdf/repayment-schedule/',
                                        PdfRepaymentScheduleAgencyView.as_view(
                                            template_name='employer_documentation/pdf-05-repayment-schedule.html',
                                            content_disposition = 'inline; filename="repayment-schedule.pdf"',
                                        ),
                                        name='pdf_agency_repayment_schedule'
                                    ),
                                    path(
                                        'pdf/rest-day-agreement/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-06-rest-day-agreement.html',
                                            content_disposition = 'inline; filename="rest-day-agreement.pdf"',
                                        ),
                                        name='pdf_agency_rest_day_agreement'
                                    ),
                                    path(
                                        'pdf/job-order/<slug:slug>/',
                                        PdfFileAgencyView.as_view(
                                            filename='job-order.pdf',
                                        ),
                                        name='pdf_agency_job_order_route'
                                    ),
                                    path(
                                        'pdf/handover-checklist/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-08-handover-checklist.html',
                                            content_disposition = 'inline; filename="handover-checklist.pdf"',
                                        ),
                                        name='pdf_agency_handover_checklist'
                                    ),
                                    path(
                                        'pdf/transfer-consent/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-09-transfer-consent.html',
                                            content_disposition = 'inline; filename="transfer-consent.pdf"',
                                        ),
                                        name='pdf_agency_transfer_consent'
                                    ),
                                    path(
                                        'pdf/work-pass-authorisation/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-10-work-pass-authorisation.html',
                                            content_disposition = 'inline; filename="work-pass-authorisation.pdf"',
                                        ),
                                        name='pdf_agency_work_pass_authorisation'
                                    ),
                                    path(
                                        'pdf/security-bond/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-11-security-bond.html',
                                            content_disposition = 'inline; filename="security-bond.pdf"',
                                        ),
                                        name='pdf_agency_security_bond'
                                    ),
                                    path(
                                        'pdf/fdw-work-permit-12b/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-12-fdw-work-permit.html',
                                            content_disposition = 'inline; filename="fdw-work-permit-form-12b.pdf"',
                                        ),
                                        name='pdf_agency_fdw_work_permit_12b'
                                    ),
                                    path(
                                        'pdf/income-tax-declaration/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-13-income-tax-declaration.html',
                                            content_disposition = 'inline; filename="income-tax-declaration.pdf"',
                                        ),
                                        name='pdf_agency_income_tax_declaration'
                                    ),
                                    path(
                                        'pdf/safety-agreement/',
                                        PdfGenericAgencyView.as_view(
                                            template_name='employer_documentation/pdf-14-safety-agreement.html',
                                            content_disposition = 'inline; filename="safety-agreement.pdf"',
                                        ),
                                        name='pdf_agency_safety_agreement'
                                    ),
                                ]),
                            ),
                        ]),
                    ),
                ]),
            ),
            path(
                'sign/<slug:slug>/',
                include([
                    path(
                        'employer/',
                        include([
                            path(
                                'verify/',
                                VerifyUserTokenView.as_view(
                                    slug_field='employer_slug',
                                    token_field_name='employer_token',
                                    success_url_route_name='token_signature_employer_route',
                                    success_message = 'Thank you for passing the verification. Please review the documents and sign below.',
                                ),
                                name='token_verification_employer_route'
                            ),
                            path(
                                'signature/',
                                SignatureUpdateByTokenView.as_view(
                                    slug_field='employer_slug',
                                    model_field_name='employer_signature',
                                    token_field_name='employer_token',
                                    form_fields=['employer_signature'],
                                    success_url_route_name='token_signature_employer_witness_route',
                                    success_message = 'Thank you for signing. Please ask your witness to enter their details and sign below.',
                                ),
                                name='token_signature_employer_route'
                            ),
                            path(
                                'witness/',
                                SignatureUpdateByTokenView.as_view(
                                    slug_field='employer_slug',
                                    model_field_name='employer_witness_signature',
                                    token_field_name='employer_token',
                                    form_fields=[
                                        'employer_witness_signature',
                                        'employer_witness_name',
                                        'employer_witness_nric',
                                    ],
                                    success_message = 'Thank you, the document submission process is complete. Please contact your agent if you have any further queries.',
                                ),
                                name='token_signature_employer_witness_route'
                            ),
                            path(
                                'pdf/',
                                include([
                                    path(
                                        'service-fees/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-01-service-fee-schedule.html',
                                            content_disposition = 'inline; filename="service_fee_schedule.pdf"',
                                        ),
                                        name='pdf_token_employer_service_fee_schedule'
                                    ),
                                    path(
                                        'service-agreement/',
                                        PdfServiceAgreementTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-03-service-agreement.html',
                                            content_disposition = 'inline; filename="service_agreement.pdf"',
                                        ),
                                        name='pdf_token_employer_service_agreement'
                                    ),
                                    path(
                                        'employment-contract/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-04-employment-contract.html',
                                            content_disposition = 'inline; filename="employment-contract.pdf"',
                                        ),
                                        name='pdf_token_employer_employment_contract'
                                    ),
                                    path(
                                        'repayment-schedule/',
                                        PdfRepaymentScheduleTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-05-repayment-schedule.html',
                                            content_disposition = 'inline; filename="repayment-schedule.pdf"',
                                        ),
                                        name='pdf_token_employer_repayment_schedule'
                                    ),
                                    path(
                                        'rest-day-agreement/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-06-rest-day-agreement.html',
                                            content_disposition = 'inline; filename="rest-day-agreement.pdf"',
                                        ),
                                        name='pdf_token_employer_rest_day_agreement'
                                    ),
                                    path(
                                        'job-order/',
                                        PdfFileTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            filename='job-order.pdf',
                                        ),
                                        name='pdf_token_employer_job_order_route'
                                    ),
                                    path(
                                        'handover-checklist/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-08-handover-checklist.html',
                                            content_disposition = 'inline; filename="handover-checklist.pdf"',
                                        ),
                                        name='pdf_token_employer_handover_checklist'
                                    ),
                                    path(
                                        'transfer-consent/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-09-transfer-consent.html',
                                            content_disposition = 'inline; filename="transfer-consent.pdf"',
                                        ),
                                        name='pdf_token_employer_transfer_consent'
                                    ),
                                    path(
                                        'work-pass-authorisation/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-10-work-pass-authorisation.html',
                                            content_disposition = 'inline; filename="work-pass-authorisation.pdf"',
                                        ),
                                        name='pdf_token_employer_work_pass_authorisation'
                                    ),
                                    path(
                                        'security-bond/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-11-security-bond.html',
                                            content_disposition = 'inline; filename="security-bond.pdf"',
                                        ),
                                        name='pdf_token_employer_security_bond'
                                    ),
                                    path(
                                        'fdw-work-permit-12b/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-12-fdw-work-permit.html',
                                            content_disposition = 'inline; filename="fdw-work-permit-form-12b.pdf"',
                                        ),
                                        name='pdf_token_employer_fdw_work_permit_12b'
                                    ),
                                    path(
                                        'income-tax-declaration/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-13-income-tax-declaration.html',
                                            content_disposition = 'inline; filename="income-tax-declaration.pdf"',
                                        ),
                                        name='pdf_token_employer_income_tax_declaration'
                                    ),
                                    path(
                                        'safety-agreement/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='employer_slug',
                                            token_field_name='employer_token',
                                            template_name='employer_documentation/pdf-14-safety-agreement.html',
                                            content_disposition = 'inline; filename="safety-agreement.pdf"',
                                        ),
                                        name='pdf_token_employer_safety_agreement'
                                    ),
                                ]),
                            ),
                        ]),
                    ),
                    path(
                    'fdw/',
                        include([
                            path(
                                'verify/',
                                VerifyUserTokenView.as_view(
                                    slug_field= 'fdw_slug',
                                    token_field_name='fdw_token',
                                    success_url_route_name='token_signature_fdw_route',
                                    success_message = 'Thank you for passing the verification. Please review the documents and sign below.',
                                ),
                                name='token_verification_fdw_route'
                            ),
                            path(
                                'signature/',
                                SignatureUpdateByTokenView.as_view(
                                    slug_field= 'fdw_slug',
                                    model_field_name='fdw_signature',
                                    token_field_name='fdw_token',
                                    form_fields=['fdw_signature'],
                                    success_url_route_name='token_signature_fdw_witness_route',
                                    success_message = 'Thank you for signing. Please ask your witness to enter their details and sign below.',
                                ),
                                name='token_signature_fdw_route'
                            ),
                            path(
                                'witness/',
                                SignatureUpdateByTokenView.as_view(
                                    slug_field= 'fdw_slug',
                                    model_field_name='fdw_witness_signature',
                                    token_field_name='fdw_token',
                                    form_fields=[
                                        'fdw_witness_signature',
                                        'fdw_witness_name',
                                        'fdw_witness_nric',
                                    ],
                                    success_message = 'Thank you, the document submission process is complete. Please contact your agent if you have any further queries.',
                                ),
                                name='token_signature_fdw_witness_route'
                            ),
                            path(
                                'pdf/',
                                include([
                                    path(
                                        'employment-contract/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='fdw_slug',
                                            token_field_name='fdw_token',
                                            template_name='employer_documentation/pdf-04-employment-contract.html',
                                            content_disposition = 'inline; filename="employment-contract.pdf"',
                                        ),
                                        name='pdf_token_fdw_employment_contract'
                                    ),
                                    path(
                                        'repayment-schedule/',
                                        PdfRepaymentScheduleTokenView.as_view(
                                            slug_field='fdw_slug',
                                            token_field_name='fdw_token',
                                            template_name='employer_documentation/pdf-05-repayment-schedule.html',
                                            content_disposition = 'inline; filename="repayment-schedule.pdf"',
                                        ),
                                        name='pdf_token_fdw_repayment_schedule'
                                    ),
                                    path(
                                        'rest-day-agreement/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='fdw_slug',
                                            token_field_name='fdw_token',
                                            template_name='employer_documentation/pdf-06-rest-day-agreement.html',
                                            content_disposition = 'inline; filename="rest-day-agreement.pdf"',
                                        ),
                                        name='pdf_token_fdw_rest_day_agreement'
                                    ),
                                    path(
                                        'job-order/',
                                        PdfFileTokenView.as_view(
                                            slug_field='fdw_slug',
                                            token_field_name='fdw_token',
                                            filename='job-order.pdf',
                                        ),
                                        name='pdf_token_fdw_job_order_route'
                                    ),
                                    path(
                                        'handover-checklist/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='fdw_slug',
                                            token_field_name='fdw_token',
                                            template_name='employer_documentation/pdf-08-handover-checklist.html',
                                            content_disposition = 'inline; filename="handover-checklist.pdf"',
                                        ),
                                        name='pdf_token_fdw_handover_checklist'
                                    ),
                                    path(
                                        'fdw-work-permit-12b/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='fdw_slug',
                                            token_field_name='fdw_token',
                                            template_name='employer_documentation/pdf-12-fdw-work-permit.html',
                                            content_disposition = 'inline; filename="fdw-work-permit-form-12b.pdf"',
                                        ),
                                        name='pdf_token_fdw_fdw_work_permit_12b'
                                    ),
                                    path(
                                        'safety-agreement/',
                                        PdfGenericTokenView.as_view(
                                            slug_field='fdw_slug',
                                            token_field_name='fdw_token',
                                            template_name='employer_documentation/pdf-14-safety-agreement.html',
                                            content_disposition = 'inline; filename="safety-agreement.pdf"',
                                        ),
                                        name='pdf_token_fdw_safety_agreement'
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
