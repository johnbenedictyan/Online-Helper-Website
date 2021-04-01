# Imports from python
import json

# Imports from django
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

# Imports from foreign installed apps
from agency.models import Agency, AgencyEmployee, AgencyPlan, AgencyBranch
from agency.mixins import (
    AgencyLoginRequiredMixin, AgencyOwnerRequiredMixin, GetAuthorityMixin
)
from enquiry.models import GeneralEnquiry
from maid.models import Maid
from payment.models import Customer, Subscription
from onlinemaid.constants import AG_OWNERS, AG_ADMINS

# Imports from local app

# Start of Views

# Template Views
class DashboardHomePage(AgencyLoginRequiredMixin, GetAuthorityMixin,
                        TemplateView):
    template_name = 'base/dashboard-home-page.html'
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        agency = Agency.objects.get(
            pk=self.agency_id
        )
        dashboard_home_page_kwargs = {
            'accounts': {
                'current': AgencyEmployee.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_employees_allowed
            },
            'biodata': {
                'current': Maid.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_biodata_allowed
            },
            'branches': {
                'current': AgencyBranch.objects.filter(
                    agency=agency
                ).count(),
                'max': None
            },
            'subscriptions': {
                'current': Subscription.objects.filter(
                    customer=Customer.objects.get(
                        agency=agency
                    )
                ).count(),
                'max': None
            },
            'employers': {
                'current': 123,
                'max': None
            },
            'sales': {
                'current': 123,
                'max': None
            },
            'enquiries': {
                'current': agency.get_enquiries().count(),
                'max': None
            }
        }
        kwargs.update(dashboard_home_page_kwargs)
        return kwargs

# Redirect Views

# List Views
class DashboardMaidList(AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'maids'
    http_method_names = ['get']
    model = Maid
    template_name = 'list/dashboard-maid-list.html'
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        agency = Agency.objects.get(
            pk=self.agency_id
        )
        kwargs.update({
            'biodata': {
                'current': Maid.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_biodata_allowed
            },
            'featured_maids': {
                'current': Maid.objects.filter(
                    agency=agency,
                    featured=True
                ).count(),
                'max': agency.amount_of_featured_biodata_allowed
            }
        })
        return kwargs
    
    def get_queryset(self):
        return Maid.objects.filter(
            agency__pk = self.agency_id
        ).order_by('id')

class DashboardAccountList(
    AgencyLoginRequiredMixin, GetAuthorityMixin, ListView):
    context_object_name = 'accounts'
    http_method_names = ['get']
    model = AgencyEmployee
    template_name = 'list/dashboard-account-list.html'
    authority = ''
    agency_id = ''

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        agency = Agency.objects.get(
            pk=self.agency_id
        )
        kwargs.update({
            'employee_accounts': {
                'current': AgencyEmployee.objects.filter(
                    agency=agency
                ).count(),
                'max': agency.amount_of_employees_allowed
            }
        })
        return kwargs
    
    def get_queryset(self):
        if self.authority == AG_OWNERS or self.authority == AG_ADMINS:
            return AgencyEmployee.objects.filter(
                agency__pk = self.agency_id
            )
        else:
            return AgencyEmployee.objects.filter(
                agency__pk = self.agency_id,
                branch = self.request.user.agency_employee.branch
            )


class DashboardAgencyPlanList(AgencyOwnerRequiredMixin, ListView):
    context_object_name = 'plans'
    http_method_names = ['get']
    model = AgencyPlan
    template_name = 'list/dashboard-agency-plan-list.html'
    
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        dashboard_agency_plan_kwargs = {
        }
        kwargs.update(dashboard_agency_plan_kwargs)
        return kwargs

class DashboardEnquiriesList(AgencyLoginRequiredMixin, ListView):
    context_object_name = 'enquiries'
    http_method_names = ['get']
    model = GeneralEnquiry
    template_name = 'list/dashboard-enquiry-list.html'

class DashboardAgencyBranchList(AgencyLoginRequiredMixin, GetAuthorityMixin,
                                ListView):
    context_object_name = 'branches'
    http_method_names = ['get']
    model = AgencyBranch
    template_name = 'list/dashboard-agency-branch-list.html'
    authority = ''
    agency_id = ''

    def get_queryset(self):
        return AgencyBranch.objects.filter(
            agency__pk = self.agency_id
        )

# Detail Views
class DashboardAgencyDetail(AgencyLoginRequiredMixin, GetAuthorityMixin,
                            DetailView):
    context_object_name = 'agency'
    http_method_names = ['get']
    model = Agency
    template_name = 'detail/dashboard-agency-detail.html'
    authority = ''
    agency_id = ''

    def get_object(self):
        agency = get_object_or_404(Agency, pk=self.agency_id)
        return agency

class DashboardMaidDetail(AgencyLoginRequiredMixin, GetAuthorityMixin,
                          DetailView):
    context_object_name = 'maid'
    http_method_names = ['get']
    model = Maid
    template_name = 'detail/dashboard-maid-detail.html'
    authority = ''
    agency_id = ''

    def get_object(self):
        return Maid.objects.get(
            pk = self.kwargs.get(
                self.pk_url_kwarg
            ),
            agency__pk = self.agency_id
        )

# Create Views

# Update Views

# Delete Views

# Generic Views
class DashboardDataProviderView(View):
    http_method_names = ['post']
    fake_data = [4568,1017,3950,3898,4364,4872,3052,4346,3884,3895,4316,1998,
                 4595,4887,4199,4518,2053,2862,3032,3752,1404,2432,3479,1108,
                 4673,2794,2890,4220,3562,3150,4128,1209,4668,2115,3094,4405,
                 3655,4254,3945,4958,3691,3850,3803,2049,2030,1851,4236,2602,
                 3161,2543,2292,3335,3732,2326,2074,1004,1258,2248,4442,4074,
                 4088,1440,2308,3257,3929,4497,3170,1454,2997,3198,4179,1393,
                 1340,1136,2356,2625,4167,3263,4235,3678,3805,4934,4806,4884,
                 1880,3598,4785,4945,1247,1463,4703,3296,1458,2785,3157,2845,
                 4158,2084,3649,3295,3246,3123,4413,4646,1278,2531,2218,3978,
                 2770,3458,3095,1289,4799,4390,2788,3549,3155,2940,2163,3355,
                 4158,3598]
    fake_sales_data = [1928.13,1654.01,1872.78,1912.47,1920.25,1223.21,1282.1,
                       1271.75,1696.94,1924.69,1261.49,1319.17,1807.36,1365.63,
                       1727.43,1055.6,1348.16,1568.3,1792.91,1294.07,1690.68,
                       1142.61,1853.0,1645.32,1341.31,1154.14,1798.84,1729.81,
                       1942.27,1202.71,1035.82,1017.09,1235.47,1190.02,1536.62,
                       1692.85,1335.03,1647.84,1867.06,1634.16,1718.82,1120.49,
                       1533.14,1355.13,1294.28,1397.56,1107.7,1736.71,1742.2,
                       1827.31,1141.72,1091.86,1359.71,1584.98,1700.06,1177.02,
                       1946.78,1732.02,1953.49,1260.4,1778.15,1561.59,1798.72,
                       1726.44,1290.43,1073.86,1132.2,1828.6,1045.69,1120.69,
                       1001.71,1377.45,1842.9,1371.19,1045.64,1810.85,1843.43,
                       1911.8,1604.64,1165.26,1148.73,1755.65,1409.31,1854.43,
                       1811.62,1212.29,1211.54,1640.7,1189.74,1107.42,1426.02,
                       1664.72,1917.44,1342.77,1019.53,1747.43,1369.28,1328.59,
                       1375.66,1186.99,1950.93,1446.33,1948.52,1120.59,1554.5,
                       1356.33,1725.75,1408.0,1674.73,1026.94,1518.31,1840.69,
                       1619.91,1855.73,1426.11,1964.36,1760.13,1126.69,1766.17,
                       1705.75]
    fake_cases_data = [16,12,8,6,11,5,6,9,3,1,3,13,8,5,6,12,2,17,2,10,4,12,5,
                       11,10,6,13,19,8,16,2,1,9,9,12,7,13,9,5,14,5,19,5,2,6,5,
                       9,5,17,4,16,17,12,6,18,19,6,12,2,13,2,7,9,5,2,10,6,11,
                       12,2,10,4,14,14,11,5,2,9,7,16,11,12,7,1,5,12,4,8,6,10,
                       11,12,5,13,4,18,13,13,5,9,9,18,7,9,15,7,20,11,9,12,4,13,
                       13,11,20,16,15,20,2,10]
    fake_branch_sales_data = [7203.69,8419.7,8230.95,9840.45,5877.32,7614.21,
                              7919.48,5403.54,6325.09,8116.59,6517.71,9828.19,
                              8632.35,5702.67,7274.22,8146.06,8446.57,9163.38,
                              5757.1,6281.02,6301.7,7759.16,7224.4,5220.92,
                              6322.76,6643.53,7529.99,6551.53,5120.07,8878.12,
                              9294.73,5194.74,8749.17,6188.3,8964.15,9950.87,
                              5056.55,7089.83,6415.79,7859.23,8783.14,9470.29,
                              8756.18,5328.67,7297.28,7814.36,5942.56,8052.46,
                              9640.71,9771.37,6753.69,7946.88,9562.48,9145.13,
                              5941.54,9267.76,9320.44,7578.25,9922.31,9648.36,
                              9222.82,5534.83,8289.89,8785.74,6196.33,7951.15,
                              5494.57,8937.8,9834.39,5595.87,8702.58,7737.33]
    fake_branch_sales_data_year = [11134.64,86113.64,81633.42,88957.0,77072.09,
                                   72969.25]
    fake_branch_cases_data = [78,72,78,79,93,52,51,100,67,65,70,88,78,76,71,50,
                              80,56,70,52,59,77,68,91,82,95,53,81,92,82,99,93,
                              76,84,67,52,79,66,76,88,75,95,99,84,51,92,81,71,
                              61,96,95,91,85,51,72,93,73,74,76,59,66,92,55,77,
                              60,85,65,64,62,85,70,75]
    fake_branch_cases_data_year = [127,49,13,81,110,113]
    
    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body.decode('utf-8'))
        chart = request_data.get('chart')
        authority = request_data.get('authority')
        if chart['name'] == 'salesChart' and authority == 'Agency Managers':
            if chart['year'] == '2010':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[0:12]
                }]
            elif chart['year'] == '2011':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[12:24]
                }]
            elif chart['year'] == '2012':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[24:36]
                }]
            elif chart['year'] == '2013':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[36:48]
                }]
            elif chart['year'] == '2014':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[48:60]
                }]
            elif chart['year'] == '2015':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[60:72]
                }]
            elif chart['year'] == '2016':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[72:84]
                }]
            elif chart['year'] == '2017':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[84:96]
                }]
            elif chart['year'] == '2018':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[96:108]
                }]
            elif chart['year'] == '2019':
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[108:120]
                }]
            else:
                chart_data = [{
                    'name': 'Sales',
                    'data': self.fake_data[120:]
                }]
                
        if chart['name'] == 'salesStaffPerformanceSales' and authority == 'Agency Managers':
            if chart['year'] == '2010':
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_sales_data[0:36:3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_sales_data[1:37:3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_sales_data[2:38:3]
                    }
                ]
            elif chart['year'] == '2011':
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_sales_data[36:72:3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_sales_data[37:73:3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_sales_data[38:74:3]
                    }
                ]
            elif chart['year'] == '2012':
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_sales_data[72:108:3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_sales_data[73:109:3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_sales_data[74:110:3]
                    }
                ]
            else:
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_sales_data[108::3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_sales_data[109::3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_sales_data[110::3]
                    }
                ]
                
        if chart['name'] == 'salesStaffPerformanceCases' and authority == 'Agency Managers':
            if chart['year'] == '2010':
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_cases_data[0:36:3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_cases_data[1:37:3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_cases_data[2:38:3]
                    }
                ]
            elif chart['year'] == '2011':
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_cases_data[36:72:3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_cases_data[37:73:3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_cases_data[38:74:3]
                    }
                ]
            elif chart['year'] == '2012':
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_cases_data[72:108:3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_cases_data[73:109:3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_cases_data[74:110:3]
                    }
                ]
            else:
                chart_data = [
                    {
                        'name': 'john',
                        'data': self.fake_cases_data[108::3]
                    },
                    {
                        'name': 'jane',
                        'data': self.fake_cases_data[109::3]
                    },
                    {
                        'name': 'dave',
                        'data': self.fake_cases_data[110::3]
                    }
                ]
                
        if chart['name'] == 'branchPerformanceSales':
            if chart['group_by'] == 'Month':
                if chart['year'] == '2010':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_sales_data[0:36:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_sales_data[1:37:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_sales_data[2:38:3]
                        }
                    ]
                elif chart['year'] == '2011':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_sales_data[36:72:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_sales_data[37:73:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_sales_data[38:74:3]
                        }
                    ]
            else:
                chart_data = [
                    {
                        'name': 'branch 1',
                        'data': self.fake_branch_sales_data_year[0::3]
                    },
                    {
                        'name': 'branch 2',
                        'data': self.fake_branch_sales_data_year[1::3]
                    },
                    {
                        'name': 'branch 3',
                        'data': self.fake_branch_sales_data_year[2::3]
                    }
                ]
                
        if chart['name'] == 'branchPerformanceCases':
            if chart['group_by'] == 'Month':
                if chart['year'] == '2010':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_cases_data[0:36:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_cases_data[1:37:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_cases_data[2:38:3]
                        }
                    ]
                elif chart['year'] == '2011':
                    chart_data = [
                        {
                            'name': 'branch 1',
                            'data': self.fake_branch_cases_data[36:72:3]
                        },
                        {
                            'name': 'branch 2',
                            'data': self.fake_branch_cases_data[37:73:3]
                        },
                        {
                            'name': 'branch 3',
                            'data': self.fake_branch_cases_data[38:74:3]
                        }
                    ]
            else:
                chart_data = [
                    {
                        'name': 'branch 1',
                        'data': self.fake_branch_cases_data_year[0::3]
                    },
                    {
                        'name': 'branch 2',
                        'data': self.fake_branch_cases_data_year[1::3]
                    },
                    {
                        'name': 'branch 3',
                        'data': self.fake_branch_cases_data_year[2::3]
                    }
                ]
        
        if chart['name'] == 'agencyTimelinePerformance':
            chart_data = [
                {
                    'name': 'Deposit',
                    'data': [3]
                },
                {
                    'name': 'IPA Approval',
                    'data': [24]
                },
                {
                    'name': 'Date of Approved Entry Application',
                    'data': [1]
                }
            ]
            
        data = {
            'name': 'Sales',
            'data': chart_data
        }
        return JsonResponse(data, status=200)