from django.urls import include, path

from .views import (CaseStatusAPIView, CaseStatusUpdateView, ChallengeFormView,
                    DocSafetyAgreementCreateView, DocSafetyAgreementUpdateView,
                    DocServAgmtEmpCtrCreateView, DocServAgmtEmpCtrUpdateView,
                    DocServiceFeeScheduleCreateView,
                    DocServiceFeeScheduleUpdateView, DocUploadCreateView,
                    DocUploadUpdateView, EmployerCreateView,
                    EmployerDeleteView, EmployerDetailView,
                    EmployerDocCreateView, EmployerDocDeleteView,
                    EmployerDocDetailView, EmployerDocJointApplicantUpdateView,
                    EmployerDocumentDetailView, EmployerDocUpdateView,
                    EmployerHouseholdDetailsFormView,
                    EmployerIncomeDetailsCreateView,
                    EmployerIncomeDetailsUpdateView,
                    EmployerJointApplicantCreateView,
                    EmployerSponsorCreateView, EmployerSponsorUpdateView,
                    EmployerUpdateView, GenerateRemainingAmountDepositReceipt,
                    HandoverFormView, HtmlToRenderPdfAgencyView,
                    HtmlToRenderPdfEmployerView, MaidInventoryFormView,
                    SignatureFormView, SignatureUpdateByAgentView,
                    UploadedPdfAgencyView)

urlpatterns = [
    path(
        'employers/',
        include([
            path(
                'create/',
                EmployerCreateView.as_view(),
                name='employer_create_route'
            ),
            path(
                '<uuid:level_0_pk>/',
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
                        'sponsor/create/',
                        EmployerSponsorCreateView.as_view(),
                        name='employer_sponsor_create_route'
                    ),
                    path(
                        'sponsor/update/',
                        EmployerSponsorUpdateView.as_view(),
                        name='employer_sponsor_update_route'
                    ),
                    path(
                        'joint-applicant/create/',
                        EmployerJointApplicantCreateView.as_view(),
                        name='employer_jointapplicant_create_route'
                    ),
                    path(
                        'joint-applicant/update/',
                        EmployerDocJointApplicantUpdateView.as_view(),
                        name='employer_jointapplicant_update_route'
                    ),
                    path(
                        'income-details/create/',
                        EmployerIncomeDetailsCreateView.as_view(),
                        name='employer_incomedetails_create_route'
                    ),
                    path(
                        'income-details/update/',
                        EmployerIncomeDetailsUpdateView.as_view(),
                        name='employer_incomedetails_update_route'
                    ),
                    path(
                        'household-details/',
                        EmployerHouseholdDetailsFormView.as_view(),
                        name='employer_householddetails_route'
                    )
                ]),
            ),
        ])
    ),
    path(
        'cases/',
        include([
            path(
                'create/',
                EmployerDocCreateView.as_view(),
                name='case_create_route'
            ),
            path(
                '<uuid:level_1_pk>/',
                include([
                    path(
                        'detail/',
                        EmployerDocDetailView.as_view(),
                        name='case_detail_route'
                    ),
                    path(
                        'update/',
                        EmployerDocUpdateView.as_view(),
                        name='case_update_route'
                    ),
                    path(
                        'delete/',
                        EmployerDocDeleteView.as_view(),
                        name='case_delete_route'
                    ),
                    path(
                        'service-fee/create/',
                        DocServiceFeeScheduleCreateView.as_view(),
                        name='servicefee_create_route'
                    ),
                    path(
                        'service-fee/update/',
                        DocServiceFeeScheduleUpdateView.as_view(),
                        name='servicefee_update_route'
                    ),
                    path(
                        'service-agreement/create/',
                        DocServAgmtEmpCtrCreateView.as_view(),
                        name='serviceagreement_create_route'
                    ),
                    path(
                        'service-agreement/update/',
                        DocServAgmtEmpCtrUpdateView.as_view(),
                        name='serviceagreement_update_route'
                    ),
                    path(
                        'safety-agreement/create/',
                        DocSafetyAgreementCreateView.as_view(),
                        name='safetyagreement_create_route'
                    ),
                    path(
                        'safety-agreement/update/',
                        DocSafetyAgreementUpdateView.as_view(),
                        name='safetyagreement_update_route'
                    ),
                    path(
                        'maid-inventory/',
                        MaidInventoryFormView.as_view(),
                        name='maid_inventory_route'
                    ),
                    path(
                        'upload-doc/create/',
                        DocUploadCreateView.as_view(),
                        name='docupload_create_route'
                    ),
                    path(
                        'upload-doc/update/',
                        DocUploadUpdateView.as_view(),
                        name='docupload_update_route'
                    ),
                    path(
                        'status/view/',
                        CaseStatusAPIView.as_view(),
                        name='case_status_api_route'
                    ),
                    path(
                        'status/update/',
                        CaseStatusUpdateView.as_view(),
                        name='case_status_update_route'
                    ),
                    path(
                        'remaining-amount/update/',
                        GenerateRemainingAmountDepositReceipt.as_view(),
                        name='servicefee_update_remaining_amount'
                    ),
                    path(
                        'pdf/',
                        include([
                            path(
                                'agency/',
                                include([
                                    # HTML to PDF - First signing event
                                    path(
                                        'service-fees/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/01-service-fee-schedule.html',
                                            content_disposition='inline; filename="service_fee_schedule.pdf"',
                                        ),
                                        name='pdf_agency_service_fee_schedule'
                                    ),
                                    path(
                                        'service-agreement/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/03-service-agreement.html',
                                            content_disposition='inline; filename="service_agreement.pdf"',
                                        ),
                                        name='pdf_agency_service_agreement'
                                    ),
                                    path(
                                        'employment-contract/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/04-employment-contract.html',
                                            content_disposition='inline; filename="employment-contract.pdf"',
                                        ),
                                        name='pdf_agency_employment_contract'
                                    ),
                                    path(
                                        'repayment-schedule/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/05-repayment-schedule.html',
                                            content_disposition='inline; filename="repayment-schedule.pdf"',
                                            use_repayment_table=True
                                        ),
                                        name='pdf_agency_repayment_schedule'
                                    ),
                                    path(
                                        'rest-day-agreement/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/06-rest-day-agreement.html',
                                            content_disposition='inline; filename="rest-day-agreement.pdf"',
                                        ),
                                        name='pdf_agency_rest_day_agreement'
                                    ),
                                    path(
                                        'transfer-consent/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/09-transfer-consent.html',
                                            content_disposition='inline; filename="transfer-consent.pdf"',
                                        ),
                                        name='pdf_agency_transfer_consent'
                                    ),
                                    path(
                                        'work-pass-authorisation/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/10-work-pass-authorisation.html',
                                            content_disposition='inline; filename="work-pass-authorisation.pdf"',
                                        ),
                                        name='pdf_agency_work_pass_authorisation'
                                    ),
                                    path(
                                        'income-tax-declaration/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/13-income-tax-declaration.html',
                                            content_disposition='inline; filename="income-tax-declaration.pdf"',
                                        ),
                                        name='pdf_agency_income_tax_declaration'
                                    ),
                                    path(
                                        'safety-agreement/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/14-safety-agreement.html',
                                            content_disposition='inline; filename="safety-agreement.pdf"',
                                        ),
                                        name='pdf_agency_safety_agreement'
                                    ),
                                    # HTML to PDF - Second signing event
                                    path(
                                        'handover-checklist/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/08-handover-checklist.html',
                                            content_disposition='inline; filename="handover-checklist.pdf"'
                                        ),
                                        name='pdf_agency_handover_checklist'
                                    ),
                                    # File to PDF
                                    path(
                                        'job-order/',
                                        UploadedPdfAgencyView.as_view(
                                            field_name='job_order_pdf',
                                            filename='job_order.pdf'
                                        ),
                                        name='pdf_agency_job_order_route'
                                    ),
                                    path(
                                        'ipa/',
                                        UploadedPdfAgencyView.as_view(
                                            field_name='ipa_pdf',
                                            filename='ipa.pdf'
                                        ),
                                        name='pdf_agency_ipa_route'
                                    ),
                                    path(
                                        'medical-report/',
                                        UploadedPdfAgencyView.as_view(
                                            field_name='medical_report_pdf',
                                            filename='medical_report.pdf'
                                        ),
                                        name='pdf_agency_medical_report_route'
                                    ),
                                    path(
                                        'deposit-invoice/',
                                        HtmlToRenderPdfAgencyView.as_view(
                                            template_name='pdf/deposit-invoice.html',
                                            content_disposition='inline; filename="deposit-invoice.pdf"'
                                        ),
                                        name='pdf_agency_deposit_invoice'
                                    ),
                                ])
                            ),
                            path(
                                'employers/',
                                include([
                                    # HTML to PDF - First signing event
                                    path(
                                        'service-fees/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/01-service-fee-schedule.html',
                                            content_disposition='inline; filename="service_fee_schedule.pdf"',
                                        ),
                                        name='pdf_employer_service_fee_schedule'
                                    ),
                                    path(
                                        'service-agreement/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/03-service-agreement.html',
                                            content_disposition='inline; filename="service_agreement.pdf"',
                                        ),
                                        name='pdf_employer_service_agreement'
                                    ),
                                    path(
                                        'employment-contract/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/04-employment-contract.html',
                                            content_disposition='inline; filename="employment-contract.pdf"',
                                        ),
                                        name='pdf_employer_employment_contract'
                                    ),
                                    path(
                                        'repayment-schedule/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/05-repayment-schedule.html',
                                            content_disposition='inline; filename="repayment-schedule.pdf"',
                                            use_repayment_table=True
                                        ),
                                        name='pdf_employer_repayment_schedule'
                                    ),
                                    path(
                                        'rest-day-agreement/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/06-rest-day-agreement.html',
                                            content_disposition='inline; filename="rest-day-agreement.pdf"',
                                        ),
                                        name='pdf_employer_rest_day_agreement'
                                    ),
                                    path(
                                        'transfer-consent/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/09-transfer-consent.html',
                                            content_disposition='inline; filename="transfer-consent.pdf"',
                                        ),
                                        name='pdf_employer_transfer_consent'
                                    ),
                                    path(
                                        'work-pass-authorisation/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/10-work-pass-authorisation.html',
                                            content_disposition='inline; filename="work-pass-authorisation.pdf"',
                                        ),
                                        name='pdf_employer_work_pass_authorisation'
                                    ),
                                    path(
                                        'income-tax-declaration/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/13-income-tax-declaration.html',
                                            content_disposition='inline; filename="income-tax-declaration.pdf"',
                                        ),
                                        name='pdf_employer_income_tax_declaration'
                                    ),
                                    path(
                                        'safety-agreement/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/14-safety-agreement.html',
                                            content_disposition='inline; filename="safety-agreement.pdf"',
                                        ),
                                        name='pdf_employer_safety_agreement'
                                    ),
                                    # HTML to PDF - Second signing event
                                    path(
                                        'handover-checklist/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/08-handover-checklist.html',
                                            content_disposition='inline; filename="handover-checklist.pdf"'
                                        ),
                                        name='pdf_employer_handover_checklist'
                                    ),
                                    # File to PDF
                                    path(
                                        'job-order/',
                                        UploadedPdfAgencyView.as_view(
                                            field_name='job_order_pdf',
                                            filename='job_order.pdf'
                                        ),
                                        name='pdf_employer_job_order_route'
                                    ),
                                    path(
                                        'ipa/',
                                        UploadedPdfAgencyView.as_view(
                                            field_name='ipa_pdf',
                                            filename='ipa.pdf'
                                        ),
                                        name='pdf_employer_ipa_route'
                                    ),
                                    path(
                                        'medical-report/',
                                        UploadedPdfAgencyView.as_view(
                                            field_name='medical_report_pdf',
                                            filename='medical_report.pdf'
                                        ),
                                        name='pdf_employer_medical_report_route'
                                    ),
                                    path(
                                        'deposit-invoice/',
                                        HtmlToRenderPdfEmployerView.as_view(
                                            template_name='pdf/deposit-invoice.html',
                                            content_disposition='inline; filename="deposit-invoice.pdf"'
                                        ),
                                        name='pdf_employer_deposit_invoice'
                                    ),
                                ])
                            )
                        ])
                    ),
                    path(
                        'sign/',
                        include([
                            # Agency signing
                            path(
                                'agency-employee/',
                                SignatureUpdateByAgentView.as_view(
                                    model_field_name='agency_staff_signature',
                                    form_fields=['agency_staff_signature'],
                                ),
                                name='signature_agencyemployee_route'
                            ),
                            path(
                                'handover-checklist/',
                                HandoverFormView.as_view(),
                                name='handover_form_view'
                            ),
                            path(
                                'employer/',
                                SignatureFormView.as_view(),
                                name='employer_form_view'
                            )
                        ]),
                    ),
                    path(
                        'view-documents/',
                        EmployerDocumentDetailView.as_view(),
                        name='employer_document_detail'
                    ),
                    path(
                        'verify/',
                        ChallengeFormView.as_view(),
                        name='employer_doc_challenge'
                    )
                ]),
            ),
        ])
    ),
    path(
        'status/',
        include([
            path(
                '<uuid:level_1_pk>/',
                include([
                    path(
                        'update/',
                        CaseStatusUpdateView.as_view(),
                        name='status_update_route'
                    ),
                ]),
            )
        ])
    ),
]
