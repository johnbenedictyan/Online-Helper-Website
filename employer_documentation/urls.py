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
                        ]),
                    ),
                ]),
            ),
        ]),
    ),
]
