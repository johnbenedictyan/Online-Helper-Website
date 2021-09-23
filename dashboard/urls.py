# Django Imports
from django.urls import include, path

# Start of urls

# List Views
from .views import (
    MaidList, AccountList, AgencyPlanList, GeneralEnquiriesList,
    AgencyBranchList, CaseList, SalesList, EmployerList, StatusList,
    ShortlistedEnquiriesList
)

# Detail Views
from .views import AgencyDetail, MaidDetail

# Form Views
from .views import (
    MaidLanguagesAndFHPDRFormView, MaidExperienceFormView,
    MaidAboutFDWFormView, AgencyOutletDetailsFormView, MaidLoanFormView,
    MaidEmploymentHistoryFormView
)
# Create Views
from .views import MaidInformationCreate, AgencyEmployeeCreate

# Template Views
from .views import HomePage

# Update Views
from .views import (
    AgencyInformationUpdate, AgencyOpeningHoursUpdate,
    AgencyEmployeeUpdate, MaidInformationUpdate
)

# Generic Views
from .views import DataProviderView

# Delete Views
from .views import (
    DashboardCaseDelete, DashboardEmployeeDelete, DashboardEmployerDelete,
    DashboardFDWDelete, DashboardSalesDelete, DashboardShortlisedEnquiryDelete,
    DashboardStatusDelete
)

# Start of Urls

urlpatterns = [
    path(
        'data/',
        DataProviderView.as_view(),
        name='dashboard_data_provider'
    ),
    path(
        'view/',
        include([
            path(
                'maids/',
                include([
                    path(
                        '',
                        MaidList.as_view(),
                        name='dashboard_maid_list'
                    ),
                    path(
                        '<int:pk>/',
                        MaidDetail.as_view(),
                        name='dashboard_maid_detail'
                    )
                ])
            ),
            path(
                'accounts/',
                AccountList.as_view(),
                name='dashboard_account_list'
            ),
            path(
                'agency-details/',
                AgencyDetail.as_view(),
                name='dashboard_agency_detail'
            ),
            path(
                'agency-plans/',
                AgencyPlanList.as_view(),
                name='dashboard_agency_plan_list'
            ),
            path(
                'general-enquiries/',
                GeneralEnquiriesList.as_view(),
                name='dashboard_general_enquiries_list'
            ),
            path(
                'shortlisted-enquiries/',
                ShortlistedEnquiriesList.as_view(),
                name='dashboard_shortlisted_enquiries_list'
            ),
            path(
                'branches/',
                AgencyBranchList.as_view(),
                name='dashboard_branches_list'
            ),
            path(
                'cases/',
                CaseList.as_view(),
                name='dashboard_case_list'
            ),
            path(
                'sales/',
                SalesList.as_view(),
                name='dashboard_sales_list'
            ),
            path(
                'status/',
                StatusList.as_view(),
                name='dashboard_status_list'
            ),
            path(
                'employers/',
                EmployerList.as_view(),
                name='dashboard_employers_list'
            )
        ])
    ),
    path(
        'create/',
        include([
            path(
                'maid/',
                MaidInformationCreate.as_view(),
                name='dashboard_maid_information_create'
            ),
            path(
                'employee/',
                AgencyEmployeeCreate.as_view(),
                name='dashboard_agency_employee_create'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                'agency-information/',
                AgencyInformationUpdate.as_view(),
                name='dashboard_agency_information_update'
            ),
            path(
                'agency-opening-hours/',
                AgencyOpeningHoursUpdate.as_view(),
                name='dashboard_agency_opening_hours_update'
            ),
            path(
                'agency-outlet-details/',
                AgencyOutletDetailsFormView.as_view(),
                name='dashboard_agency_outlet_details_update'
            ),
            path(
                'agency-employee/<int:pk>/',
                AgencyEmployeeUpdate.as_view(),
                name='dashboard_agency_employee_update'
            ),
            path(
                'maid/<int:pk>/',
                include([
                    path(
                        '',
                        MaidInformationUpdate.as_view(),
                        name='dashboard_maid_information_update'
                    ),
                    path(
                        'languages-and-food-handling-dietary-restriction/',
                        MaidLanguagesAndFHPDRFormView.as_view(),
                        name='dashboard_maid_languages_and_fhpdr_update'
                    ),
                    path(
                        'experience/',
                        MaidExperienceFormView.as_view(),
                        name='dashboard_maid_experience_update'
                    ),
                    path(
                        'about-fdw/',
                        MaidAboutFDWFormView.as_view(),
                        name='dashboard_maid_about_fdw_update'
                    ),
                    path(
                        'employment-history/',
                        MaidEmploymentHistoryFormView.as_view(),
                        name='dashboard_maid_employment_history_update'
                    ),
                    path(
                        'loan/',
                        MaidLoanFormView.as_view(),
                        name='dashboard_maid_loan_update'
                    )
                ])
            )
        ])
    ),
    path(
        '',
        HomePage.as_view(),
        name='dashboard_home'
    )
]
