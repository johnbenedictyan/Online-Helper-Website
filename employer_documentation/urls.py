# Imports from django
from django.urls import include, path

from . import views, models

# Start of Urls
urlpatterns = [
    path(
        'employers/',
        include([
            path(
                'create/',
                views.EmployerCreateView.as_view(),
                name='employer_create_route'
            ),
            path(
                '<uuid:level_0_pk>/',
                include([
                    path(
                        'detail/',
                        views.EmployerDetailView.as_view(),
                        name='employer_detail_route'
                    ),
                    path(
                        'update/',
                        views.EmployerUpdateView.as_view(),
                        name='employer_update_route'
                    ),
                    path(
                        'delete/',
                        views.EmployerDeleteView.as_view(),
                        name='employer_delete_route'
                    ),
                    path(
                        'sponsor/create/',
                        views.EmployerSponsorCreateView.as_view(),
                        name='employer_sponsor_create_route'
                    ),
                    path(
                        'sponsor/update/',
                        views.EmployerSponsorUpdateView.as_view(),
                        name='employer_sponsor_update_route'
                    ),
                    path(
                        'joint-applicant/create/',
                        views.EmployerJointApplicantCreateView.as_view(),
                        name='employer_jointapplicant_create_route'
                    ),
                    path(
                        'joint-applicant/update/',
                        views.EmployerDocJointApplicantUpdateView.as_view(),
                        name='employer_jointapplicant_update_route'
                    ),
                    path(
                        'income-details/create/',
                        views.EmployerIncomeDetailsCreateView.as_view(),
                        name='employer_incomedetails_create_route'
                    ),
                    path(
                        'income-details/update/',
                        views.EmployerIncomeDetailsUpdateView.as_view(),
                        name='employer_incomedetails_update_route'
                    ),
                    path(
                        'household-details/',
                        views.EmployerHouseholdDetailsFormView.as_view(),
                        name='employer_householddetails_update_route'
                    )
                ]),
            ),
        ]),
    ),
    path(
        'cases/',
        include([
            path(
                'create/',
                views.EmployerDocCreateView.as_view(),
                name='case_create_route'
            ),
            path(
                '<uuid:level_1_pk>/',
                include([
                    path(
                        'detail/',
                        views.EmployerDocDetailView.as_view(),
                        name='case_detail_route'
                    ),
                    path(
                        'update/',
                        views.EmployerDocUpdateView.as_view(),
                        name='case_update_route'
                    ),
                    path(
                        'delete/',
                        views.EmployerDocDeleteView.as_view(),
                        name='case_delete_route'
                    ),
                    path(
                        'service-fee/create/',
                        views.DocServiceFeeScheduleCreateView.as_view(),
                        name='servicefee_create_route'
                    ),
                    path(
                        'service-fee/update/',
                        views.DocServiceFeeScheduleUpdateView.as_view(),
                        name='servicefee_update_route'
                    ),
                    path(
                        'service-agreement/create/',
                        views.DocServAgmtEmpCtrCreateView.as_view(),
                        name='serviceagreement_create_route'
                    ),
                    path(
                        'service-agreement/update/',
                        views.DocServAgmtEmpCtrUpdateView.as_view(),
                        name='serviceagreement_update_route'
                    ),
                    path(
                        'safety-agreement/create/',
                        views.DocSafetyAgreementCreateView.as_view(),
                        name='safetyagreement_create_route'
                    ),
                    path(
                        'safety-agreement/update/',
                        views.DocSafetyAgreementUpdateView.as_view(),
                        name='safetyagreement_update_route'
                    ),
                    path(
                        'upload-doc/create/',
                        views.DocUploadCreateView.as_view(),
                        name='docupload_create_route'
                    ),
                    path(
                        'upload-doc/update/',
                        views.DocUploadUpdateView.as_view(),
                        name='docupload_update_route'
                    ),
                    path(
                        'status/view/',
                        views.CaseStatusAPIView.as_view(),
                        name='case_status_api_route'
                    ),
                    path(
                        'status/update/',
                        views.CaseStatusUpdateView.as_view(),
                        name='case_status_update_route'
                    ),
                    path(
                        'signature/generate-url/',
                        include([
                            path(
                                'employer/',
                                views.GenerateSigSlugEmployer1View.as_view(),
                                name='sigslug_employer1_generate_route'
                            ),
                            path(
                                'employer-spouse/',
                                views.GenerateSigSlugEmployerSpouseView.as_view(),
                                name='sigslug_employer_spouse_generate_route'
                            ),
                            path(
                                'sponsor-1/',
                                views.GenerateSigSlugSponsor1View.as_view(),
                                name='sigslug_sponsor1_generate_route'
                            ),
                            path(
                                'sponsor-2/',
                                views.GenerateSigSlugSponsor2View.as_view(),
                                name='sigslug_sponsor2_generate_route'
                            ),
                            path(
                                'joint-applicant/',
                                views.GenerateSigSlugJointApplicantView.as_view(),
                                name='sigslug_joint_applicant_generate_route'
                            )
                        ])
                    ),
                    path(
                        'signature/revoke-url/',
                        include([
                            path(
                                'employer/',
                                views.RevokeSigSlugEmployer1View.as_view(),
                                name='sigslug_employer1_revoke_route'
                            ),
                            path(
                                'employer-spouse/',
                                views.RevokeSigSlugEmployerSpouseView.as_view(),
                                name='sigslug_employer_spouse_revoke_route'
                            ),
                            path(
                                'sponsor-1/',
                                views.RevokeSigSlugSponsor1View.as_view(),
                                name='sigslug_sponsor1_revoke_route'
                            ),
                            path(
                                'sponsor-2/',
                                views.RevokeSigSlugSponsor2View.as_view(),
                                name='sigslug_sponsor2_revoke_route'
                            ),
                            path(
                                'joint-applicant/',
                                views.RevokeSigSlugJointApplicantView.as_view(),
                                name='sigslug_joint_applicant_revoke_route'
                            )
                        ])
                    ),
                    path(
                        'archive/',
                        views.ArchiveCase.as_view(),
                        name='doc_archive'
                    ),
                    path(
                        'pdf/',
                        include([
                            # HTML to PDF - First signing event
                            path(
                                'service-fees/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/01-service-fee-schedule.html',
                                    content_disposition = 'inline; filename="service_fee_schedule.pdf"',
                                ),
                                name='pdf_agency_service_fee_schedule'
                            ),
                            path(
                                'service-agreement/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/03-service-agreement.html',
                                    content_disposition = 'inline; filename="service_agreement.pdf"',
                                ),
                                name='pdf_agency_service_agreement'
                            ),
                            path(
                                'employment-contract/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/04-employment-contract.html',
                                    content_disposition = 'inline; filename="employment-contract.pdf"',
                                ),
                                name='pdf_agency_employment_contract'
                            ),
                            path(
                                'repayment-schedule/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/05-repayment-schedule.html',
                                    content_disposition = 'inline; filename="repayment-schedule.pdf"',
                                    use_repayment_table = True,
                                ),
                                name='pdf_agency_repayment_schedule'
                            ),
                            path(
                                'rest-day-agreement/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/06-rest-day-agreement.html',
                                    content_disposition = 'inline; filename="rest-day-agreement.pdf"',
                                ),
                                name='pdf_agency_rest_day_agreement'
                            ),
                            path(
                                'transfer-consent/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/09-transfer-consent.html',
                                    content_disposition = 'inline; filename="transfer-consent.pdf"',
                                ),
                                name='pdf_agency_transfer_consent'
                            ),
                            path(
                                'work-pass-authorisation/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/10-work-pass-authorisation.html',
                                    content_disposition = 'inline; filename="work-pass-authorisation.pdf"',
                                ),
                                name='pdf_agency_work_pass_authorisation'
                            ),
                            path(
                                'income-tax-declaration/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/13-income-tax-declaration.html',
                                    content_disposition = 'inline; filename="income-tax-declaration.pdf"',
                                ),
                                name='pdf_agency_income_tax_declaration'
                            ),
                            path(
                                'safety-agreement/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/14-safety-agreement.html',
                                    content_disposition = 'inline; filename="safety-agreement.pdf"',
                                ),
                                name='pdf_agency_safety_agreement'
                            ),
                            # HTML to PDF - Second signing event
                            path(
                                'handover-checklist/',
                                views.HtmlToRenderPdfAgencyView.as_view(
                                    template_name='employer_documentation/pdf/08-handover-checklist.html',
                                    content_disposition = 'inline; filename="handover-checklist.pdf"',
                                ),
                                name='pdf_agency_handover_checklist'
                            ),
                            # File to PDF
                            path(
                                'job-order/',
                                views.UploadedPdfAgencyView.as_view(
                                    model=models.DocUpload,
                                    pk_url_kwarg = 'level_1_pk',
                                    field_name = 'job_order_pdf',
                                    filename='job_order.pdf',
                                ),
                                name='pdf_agency_job_order_route'
                            ),
                            path(
                                'ipa/',
                                views.UploadedPdfAgencyView.as_view(
                                    model=models.DocUpload,
                                    pk_url_kwarg = 'level_1_pk',
                                    field_name = 'ipa_pdf',
                                    filename='ipa.pdf',
                                ),
                                name='pdf_agency_ipa_route'
                            ),
                            path(
                                'e-issuance/',
                                views.UploadedPdfAgencyView.as_view(
                                    model=models.DocUpload,
                                    pk_url_kwarg = 'level_1_pk',
                                    field_name = 'e_issuance_pdf',
                                    filename='e_issuance.pdf',
                                ),
                                name='pdf_agency_e_issuance_route'
                            ),
                            path(
                                'medical-report/',
                                views.UploadedPdfAgencyView.as_view(
                                    model=models.DocUpload,
                                    pk_url_kwarg = 'level_1_pk',
                                    field_name = 'medical_report_pdf',
                                    filename='medical_report.pdf',
                                ),
                                name='pdf_agency_medical_report_route'
                            ),
                            ################################## Deprecated
                            # path(
                            #     'pdf/security-bond/',
                            #     views.HtmlToRenderPdfAgencyView.as_view(
                            #         template_name='employer_documentation/pdf/11-security-bond.html',
                            #         content_disposition = 'inline; filename="security-bond.pdf"',
                            #     ),
                            #     name='pdf_agency_security_bond'
                            # ),
                            # path(
                            #     'pdf/fdw-work-permit-12b/',
                            #     views.HtmlToRenderPdfAgencyView.as_view(
                            #         template_name='employer_documentation/pdf/12-fdw-work-permit.html',
                            #         content_disposition = 'inline; filename="fdw-work-permit-form-12b.pdf"',
                            #     ),
                            #     name='pdf_agency_fdw_work_permit_12b'
                            # ),
                            # path(
                            #     'sponsor-details/',
                            #     views.HtmlToRenderPdfAgencyView.as_view(
                            #         template_name='employer_documentation/pdf/15-MoM-work-permit-sponsors.html',
                            #         content_disposition = 'inline; filename="sponsor-details.pdf"',
                            #     ),
                            #     name='pdf_agency_sponsor_details'
                            # ),
                            # path(
                            #     'joint-applicant/',
                            #     views.HtmlToRenderPdfAgencyView.as_view(
                            #         template_name='employer_documentation/pdf/16-MoM-work-permit-joint-applicant.html',
                            #         content_disposition = 'inline; filename="joint-applicant-details.pdf"',
                            #     ),
                            #     name='pdf_agency_joint_applicants'
                            # ),
                            ################################## Deprecated
                        ]),
                    ),
                    path(
                        'sign/',
                        include([
                            # Agency signing
                            path(
                                'agency-employee/',
                                views.SignatureUpdateByAgentView.as_view(
                                    model_field_name='agency_staff_signature',
                                    form_fields=['agency_staff_signature'],
                                ),
                                name='signature_agencyemployee_route'
                            ),
                        ]),
                    ),
    #                 path(
    #                     '<int:level_2_pk>/employer-url/',
    #                     views.CaseSignatureSlugUpdateView.as_view(
    #                         model_field_name='sigslug_employer_1',
    #                         form_fields=['sigslug_employer_1'],
    #                         success_url_route_name='sig_slug_employer_update_route',
    #                     ),
    #                     name='sig_slug_employer_update_route'
    #                 ),
    #                 path(
    #                     '<int:level_2_pk>/fdw-url/',
    #                     views.CaseSignatureSlugUpdateView.as_view(
    #                         model_field_name='fdw_slug',
    #                         form_fields=['fdw_slug'],
    #                         success_url_route_name='sig_slug_fdw_update_route',
    #                     ),
    #                     name='sig_slug_fdw_update_route'
    #                 ),
    #                 path(
    #                     'signature/<int:level_2_pk>/',
    #                     include([
    #                         path(
    #                             'agent-access/employer/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='employer_signature',
    #                                 form_fields=['employer_signature'],
    #                             ),
    #                             name='signature_employer_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/employer-witness/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='employer_witness_signature',
    #                                 form_fields=[
    #                                     'employer_witness_signature',
    #                                     'employer_witness_name',
    #                                     'employer_witness_nric',
    #                                     'employer_witness_address_1',
    #                                     'employer_witness_address_2',
    #                                     'employer_witness_post_code',
    #                                 ],
    #                             ),
    #                             name='signature_employer_witness_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/spouse/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='spouse_signature',
    #                                 form_fields=[
    #                                     'spouse_signature',
    #                                     # 'spouse_name',
    #                                     # 'spouse_nric',
    #                                 ],
    #                             ),
    #                             name='signature_spouse_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/sponsor-1/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='sponsor_1_signature',
    #                                 form_fields=['sponsor_1_signature'],
    #                             ),
    #                             name='signature_sponsor_1_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/sponsor-2/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='sponsor_2_signature',
    #                                 form_fields=['sponsor_2_signature'],
    #                             ),
    #                             name='signature_sponsor_2_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/joint-applicant/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='joint_applicant_signature',
    #                                 form_fields=['joint_applicant_signature'],
    #                             ),
    #                             name='signature_joint_applicant_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/fdw/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='fdw_signature',
    #                                 form_fields=['fdw_signature'],
    #                             ),
    #                             name='signature_fdw_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/fdw-witness/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='fdw_witness_signature',
    #                                 form_fields=[
    #                                     'fdw_witness_signature',
    #                                     'fdw_witness_name',
    #                                     'fdw_witness_nric',
    #                                 ],
    #                             ),
    #                             name='signature_fdw_witness_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/agency-staff/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='agency_staff_signature',
    #                                 form_fields=['agency_staff_signature'],
    #                             ),
    #                             name='signature_agency_staff_update_route'
    #                         ),
    #                         path(
    #                             'agent-access/agency-staff-witness/update/',
    #                             views.SignatureUpdateByAgentView.as_view(
    #                                 model_field_name='agency_staff_witness_signature',
    #                                 form_fields=[
    #                                     'agency_staff_witness_signature',
    #                                     'agency_staff_witness_name',
    #                                     'agency_staff_witness_nric',
    #                                 ],
    #                             ),
    #                             name='signature_agency_staff_witness_update_route'
    #                         ),
    #                     ]),
    #                 ),
    #                 path(
    #                     'archive/',
    #                     include([
    #                         path(
    #                             'save/',
    #                             views.PdfArchiveSaveView.as_view(),
    #                             name='pdf_archive_save'
    #                         ),
    #                         path(
    #                             'detail/',
    #                             views.PdfArchiveDetailView.as_view(),
    #                             name='pdf_archive_detail'
    #                         ),
    #                         path(
    #                             'service-fees/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f01_service_fee_schedule',
    #                             ),
    #                             name='pdf_archive_service_fees'
    #                         ),
    #                         path(
    #                             'service-agreement/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f03_service_agreement',
    #                             ),
    #                             name='pdf_archive_service_agreement'
    #                         ),
    #                         path(
    #                             'employment-contract/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f04_employment_contract',
    #                             ),
    #                             name='pdf_archive_employment_contract'
    #                         ),
    #                         path(
    #                             'repayment-schedule/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f05_repayment_schedule',
    #                             ),
    #                             name='pdf_archive_repayment_schedule'
    #                         ),
    #                         path(
    #                             'rest-day-agreement/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f06_rest_day_agreement',
    #                             ),
    #                             name='pdf_archive_rest_day_agreement'
    #                         ),
    #                         path(
    #                             'handover-checklist/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f08_handover_checklist',
    #                             ),
    #                             name='pdf_archive_handover_checklist'
    #                         ),
    #                         path(
    #                             'transfer-consent/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f09_transfer_consent',
    #                             ),
    #                             name='pdf_archive_transfer_consent'
    #                         ),
    #                         path(
    #                             'work-pass-authorisation/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f10_work_pass_authorisation',
    #                             ),
    #                             name='pdf_archive_work_pass_authorisation'
    #                         ),
    #                         # path(
    #                         #     'security-bond/',
    #                         #     views.UploadedPdfAgencyView.as_view(
    #                         #         model=models.EmployerDoc,
    #                         #         pk_url_kwarg='level_1_pk',
    #                         #         field_name='f11_security_bond',
    #                         #     ),
    #                         #     name='pdf_archive_security_bond'
    #                         # ),
    #                         # path(
    #                         #     'fdw-work-permit-12b/',
    #                         #     views.UploadedPdfAgencyView.as_view(
    #                         #         model=models.EmployerDoc,
    #                         #         pk_url_kwarg='level_1_pk',
    #                         #         field_name='f12_fdw_work_permit',
    #                         #     ),
    #                         #     name='pdf_archive_fdw_work_permit'
    #                         # ),
    #                         path(
    #                             'income-tax-declaration/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f13_income_tax_declaration',
    #                             ),
    #                             name='pdf_archive_income_tax_declaration'
    #                         ),
    #                         path(
    #                             'safety-agreement/',
    #                             views.UploadedPdfAgencyView.as_view(
    #                                 model=models.EmployerDoc,
    #                                 pk_url_kwarg='level_1_pk',
    #                                 field_name='f14_safety_agreement',
    #                             ),
    #                             name='pdf_archive_safety_agreement'
    #                         ),
    #                     ]),
    #                 ),
                ]),
            ),
        ]),
    ),
    # path(
    #     'token/<slug:slug>/',
    #     include([
    #         path(
    #             'employer/',
    #             include([
    #                 path(
    #                     'verify/',
    #                     views.VerifyUserTokenView.as_view(
    #                         slug_field='sigslug_employer_1',
    #                         token_field_name='employer_token',
    #                         success_url_route_name='token_signature_employer_route',
    #                         success_message = 'Thank you for passing the verification. Please review the documents and sign below.',
    #                     ),
    #                     name='token_verification_employer_route'
    #                 ),
    #                 path(
    #                     'signature/',
    #                     views.SignatureUpdateByTokenView.as_view(
    #                         slug_field='sigslug_employer_1',
    #                         model_field_name='employer_signature',
    #                         token_field_name='employer_token',
    #                         form_fields=['employer_signature'],
    #                         success_url_route_name='token_signature_employer_witness_route',
    #                         success_message = 'Thank you for signing. Please ask your witness to enter their details and sign below.',
    #                     ),
    #                     name='token_signature_employer_route'
    #                 ),
    #                 path(
    #                     'witness/',
    #                     views.SignatureUpdateByTokenView.as_view(
    #                         slug_field='sigslug_employer_1',
    #                         model_field_name='employer_witness_signature',
    #                         token_field_name='employer_token',
    #                         form_fields=[
    #                             'employer_witness_signature',
    #                             'employer_witness_name',
    #                             'employer_witness_nric',
    #                             'employer_witness_address_1',
    #                             'employer_witness_address_2',
    #                             'employer_witness_post_code',
    #                         ],
    #                         success_url_route_name='token_signature_employer_spouse_route',
    #                         success_message = 'Thank you.',
    #                     ),
    #                     name='token_signature_employer_witness_route'
    #                 ),
    #                 path(
    #                     'spouse/',
    #                     views.SignatureUpdateByTokenView.as_view(
    #                         slug_field='sigslug_employer_1',
    #                         model_field_name='spouse_signature',
    #                         token_field_name='employer_token',
    #                         form_fields=[
    #                             'spouse_signature',
    #                             # 'spouse_name',
    #                             # 'spouse_nric',
    #                         ],
    #                         success_message = 'Thank you.',
    #                     ),
    #                     name='token_signature_employer_spouse_route'
    #                 ),
    #                 ),
    #             ]),
    #         ),
    #     ]),
    # ),
    # path('sales/',
    #     include([
    #         path(
    #             'sales-list/',
    #             views.DocListView.as_view(
    #                 template_name = 'employer_documentation/sales_list.html',
    #                 is_deployed=True,
    #             ),
    #             name='dashboard_sales_list'
    #         ),
    #     ]),
    # ),
    path(
        'token/',
        include([
            path(
                '<slug:slug>/',
                include([
                    path(
                        'verification/',
                        views.TokenChallengeView.as_view(),
                        name='token_challenge_route'
                    ),
                    path(
                        'sign/',
                        include([
                            path(
                                'employer/',
                                views.EmployerSignatureFormView.as_view(),
                                name='token_employer_signature_form_view'
                            ),
                            path(
                                'employer-with-spouse/',
                                views.EmployerWithSpouseSignatureFormView.as_view(),
                                name='token_employer_with_spouse_signature_form_view'
                            ),
                            path(
                                'employer-spouse/',
                                views.EmployerSpouseSignatureFormView.as_view(),
                                name='token_employer_spouse_signature_form_view'
                            ),
                            path(
                                'sponsor-1/',
                                views.Sponsor1SignatureFormView.as_view(),
                                name='token_sponsor_1_signature_form_view'
                            ),
                            path(
                                'sponsor-2/',
                                views.Sponsor2SignatureFormView.as_view(),
                                name='token_sponsor_2_signature_form_view'
                            ),
                            path(
                                'joint-applicant/',
                                views.JointApplicantSignatureFormView.as_view(),
                                name='token_joint_applicant_signature_form_view'
                            ),
                        ]),
                    ),
                    path(
                        'pdf/',
                        include([
                            path(
                                'service-fees/',
                                views.HtmlToRenderPdfTokenView.as_view(
                                    template_name = 'employer_documentation/pdf/01-service-fee-schedule.html',
                                    content_disposition = 'inline; filename="service_fee_schedule.pdf"',
                                ),
                                name='pdf_token_employer_service_fee_schedule'
                            ),
    #                         path(
    #                             'service-agreement/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/03-service-agreement.html',
    #                                 content_disposition = 'inline; filename="service_agreement.pdf"',
    #                             ),
    #                             name='pdf_token_employer_service_agreement'
    #                         ),
    #                         path(
    #                             'employment-contract/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/04-employment-contract.html',
    #                                 content_disposition = 'inline; filename="employment-contract.pdf"',
    #                             ),
    #                             name='pdf_token_employer_employment_contract'
    #                         ),
    #                         path(
    #                             'repayment-schedule/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/05-repayment-schedule.html',
    #                                 content_disposition = 'inline; filename="repayment-schedule.pdf"',
    #                                 use_repayment_table = True,
    #                             ),
    #                             name='pdf_token_employer_repayment_schedule'
    #                         ),
    #                         path(
    #                             'rest-day-agreement/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/06-rest-day-agreement.html',
    #                                 content_disposition = 'inline; filename="rest-day-agreement.pdf"',
    #                             ),
    #                             name='pdf_token_employer_rest_day_agreement'
    #                         ),
    #                         path(
    #                             'job-order/',
    #                             views.PdfFileTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 filename='job-order.pdf',
    #                             ),
    #                             name='pdf_token_employer_job_order_route'
    #                         ),
    #                         path(
    #                             'handover-checklist/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/08-handover-checklist.html',
    #                                 content_disposition = 'inline; filename="handover-checklist.pdf"',
    #                             ),
    #                             name='pdf_token_employer_handover_checklist'
    #                         ),
    #                         path(
    #                             'transfer-consent/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/09-transfer-consent.html',
    #                                 content_disposition = 'inline; filename="transfer-consent.pdf"',
    #                             ),
    #                             name='pdf_token_employer_transfer_consent'
    #                         ),
    #                         path(
    #                             'work-pass-authorisation/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/10-work-pass-authorisation.html',
    #                                 content_disposition = 'inline; filename="work-pass-authorisation.pdf"',
    #                             ),
    #                             name='pdf_token_employer_work_pass_authorisation'
    #                         ),
    #                         # path(
    #                         #     'security-bond/',
    #                         #     views.PdfGenericTokenView.as_view(
    #                         #         slug_field='sigslug_employer_1',
    #                         #         token_field_name='employer_token',
    #                         #         template_name='employer_documentation/pdf/11-security-bond.html',
    #                         #         content_disposition = 'inline; filename="security-bond.pdf"',
    #                         #     ),
    #                         #     name='pdf_token_employer_security_bond'
    #                         # ),
    #                         # path(
    #                         #     'fdw-work-permit-12b/',
    #                         #     views.PdfGenericTokenView.as_view(
    #                         #         slug_field='sigslug_employer_1',
    #                         #         token_field_name='employer_token',
    #                         #         template_name='employer_documentation/pdf/12-fdw-work-permit.html',
    #                         #         content_disposition = 'inline; filename="fdw-work-permit-form-12b.pdf"',
    #                         #     ),
    #                         #     name='pdf_token_employer_fdw_work_permit_12b'
    #                         # ),
    #                         path(
    #                             'income-tax-declaration/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/13-income-tax-declaration.html',
    #                                 content_disposition = 'inline; filename="income-tax-declaration.pdf"',
    #                             ),
    #                             name='pdf_token_employer_income_tax_declaration'
    #                         ),
    #                         path(
    #                             'safety-agreement/',
    #                             views.PdfGenericTokenView.as_view(
    #                                 slug_field='sigslug_employer_1',
    #                                 token_field_name='employer_token',
    #                                 template_name='employer_documentation/pdf/14-safety-agreement.html',
    #                                 content_disposition = 'inline; filename="safety-agreement.pdf"',
    #                             ),
    #                             name='pdf_token_employer_safety_agreement'
    #                         ),
                        ]),
                    ),
                ]),
            ),
        ]),
    ),
    path('status/',
        include([
            path(
                '<uuid:level_1_pk>/',
                include([
                    path(
                        'update/',
                        views.CaseStatusUpdateView.as_view(),
                        name='status_update_route'
                    ),
                ]),
            ),
        ]),
    ),
]
