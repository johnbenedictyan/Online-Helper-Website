# Imports from django
from django.urls import include, path

# Imports from foreign installed apps

# Imports from local app

## Redirect Views

## List Views
from .views import (
    DashboardMaidList, DashboardAccountList, DashboardAgencyPlanList,
    DashboardGeneralEnquiriesList, DashboardAgencyBranchList, DashboardCaseList,
    DashboardSalesList, DashboardEmployerList, DashboardStatusList, 
    DashboardShortlistedEnquiriesList
)

## Detail Views
from .views import (
    DashboardAgencyDetail, DashboardMaidDetail, DashboardEmployerDetail,
    DashboardCaseDetail
)

## Form Views
from .views import (
    DashboardMaidCreation, DashboardAgencyUpdate,
    DashboardMaidLanguageSpokenFormView, DashboardMaidLanguagesAndFHPDRFormView,
    DashboardMaidExperienceFormView, DashboardMaidAboutFDWFormView,
    DashboardAgencyOutletDetailsFormView, DashboardMaidLoanFormView,
    DashboardMaidEmploymentHistoryFormView
)
## Create Views
from .views import (
    DashboardMaidInformationCreate, DashboardAgencyEmployeeCreate
)

## Template Views
from .views import DashboardHomePage

## Update Views
from .views import (
    DashboardAgencyInformationUpdate, DashboardAgencyOpeningHoursUpdate,
    DashboardAgencyEmployeeUpdate, DashboardMaidInformationUpdate
)

## Delete Views

## Generic Views
from .views import DashboardDataProviderView

# Start of Urls

urlpatterns = [
    path(
        'data/',
        DashboardDataProviderView.as_view(),
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
                        DashboardMaidList.as_view(),
                        name='dashboard_maid_list'
                    ),
                    path(
                        '<int:pk>/',
                        DashboardMaidDetail.as_view(),
                        name='dashboard_maid_detail'
                    )
                ])
            ),
            path(
                'accounts/',
                DashboardAccountList.as_view(),
                name='dashboard_account_list'
            ),
            path(
                'agency-details/',
                DashboardAgencyDetail.as_view(),
                name='dashboard_agency_detail'
            ),
            path(
                'agency-plans/',
                DashboardAgencyPlanList.as_view(),
                name='dashboard_agency_plan_list'
            ),
            path(
                'general-enquiries/',
                DashboardGeneralEnquiriesList.as_view(),
                name='dashboard_general_enquiries_list'
            ),
            path(
                'shortlisted-enquiries/',
                DashboardShortlistedEnquiriesList.as_view(),
                name='dashboard_shortlisted_enquiries_list'
            ),
            path(
                'branches/',
                DashboardAgencyBranchList.as_view(),
                name='dashboard_branches_list'
            ),
            path(
                'cases/',
                DashboardCaseList.as_view(),
                name='dashboard_case_list'
            ),
            path(
                'sales/',
                DashboardSalesList.as_view(),
                name='dashboard_sales_list'
            ),
            path(
                'status/',
                DashboardStatusList.as_view(),
                name='dashboard_status_list'
            ),
            path(
                'employers/',
                DashboardEmployerList.as_view(),
                name='dashboard_employers_list'
            )
        ])
    ),
    path(
        'create/',
        include([
            path(
                'maid/',
                DashboardMaidInformationCreate.as_view(),
                name='dashboard_maid_information_create'
            ),
            path(
                'employee/',
                DashboardAgencyEmployeeCreate.as_view(),
                name='dashboard_agency_employee_create'
            )
        ])
    ),
    path(
        'update/',
        include([
            path(
                'agency/',
                DashboardAgencyUpdate.as_view(),
                name='dashboard_agency_update'
            ),
            path(
                'agency-information/',
                DashboardAgencyInformationUpdate.as_view(),
                name='dashboard_agency_information_update'
            ),
            path(
                'agency-opening-hours/',
                DashboardAgencyOpeningHoursUpdate.as_view(),
                name='dashboard_agency_opening_hours_update'
            ),
            path(
                'agency-outlet-details/',
                DashboardAgencyOutletDetailsFormView.as_view(),
                name='dashboard_agency_outlet_details_update'
            ),
            path(
                'agency-employee/<int:pk>/',
                DashboardAgencyEmployeeUpdate.as_view(),
                name='dashboard_agency_employee_update'
            ),
            path(
                'maid/<int:pk>/',
                include([
                    path(
                        '',
                        DashboardMaidInformationUpdate.as_view(),
                        name='dashboard_maid_information_update'
                    ),
                    # path(
                    #     'language-spoken/',
                    #     DashboardMaidLanguageSpokenFormView.as_view(),
                    #     name='dashboard_maid_language_spoken_update'
                    # ),
                    path(
                        'languages-and-food-handling-dietary-restriction/',
                        DashboardMaidLanguagesAndFHPDRFormView.as_view(),
                        name='dashboard_maid_languages_and_fhpdr_update'
                    ),
                    path(
                        'experience/',
                        DashboardMaidExperienceFormView.as_view(),
                        name='dashboard_maid_experience_update'
                    ),
                    path(
                        'about-fdw/',
                        DashboardMaidAboutFDWFormView.as_view(),
                        name='dashboard_maid_about_fdw_update'
                    ),
                    path(
                        'employment-history/',
                        DashboardMaidEmploymentHistoryFormView.as_view(),
                        name='dashboard_maid_employment_history_update'
                    ),
                    path(
                        'loan/',
                        DashboardMaidLoanFormView.as_view(),
                        name='dashboard_maid_loan_update'
                    )
                ])
            )
        ])
    ),
    path(
        '',
        DashboardHomePage.as_view(),
        name='dashboard_home'
    )
]
