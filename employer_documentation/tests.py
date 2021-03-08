from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, Group

import accounts
from agency.models import Agency, AgencyBranch, AgencyOwner, AgencyEmployee
from .views import *

class SetUp():
    '''
    Setup class to populate test database with agency, users, etc
    '''
    def setUp(self):
        self.factory = RequestFactory()

        group_choices = {
            'AO': 'Agency Owners',
            'AA': 'Agency Administrators',
            'AM': 'Agency Managers',
            'AS': 'Agency Sales Staff',
            'PE': 'Potential Employer',
        }
        for k,v in group_choices.items():
            instance = Group(name=v)
            setattr(self, k, instance)
            instance.save()

        self.user_potential_employer = accounts.models.User(
            email='user_potential_employer@e.com',
            password='12345678',
            is_online=True,
        )
        self.user_potential_employer.save()
        self.user_potential_employer.groups.set([self.PE])

        self.potential_employer = accounts.models.Employer(
            user=self.user_potential_employer,
            first_name='first_name',
            last_name='last_name',
            contact_number='91919191',
        )
        self.potential_employer.save()

        self.agency = Agency(
            company_email = 'a@a.com',
            sales_email = 'a@a.com',
            name = 'AAA Agency Pte Ltd',
            license_number = '12345',
            website_uri = 'https://a.com',
            uen = '98765',
            mission = 'Custom mission',
        )
        self.agency.save()

        self.branch = AgencyBranch(
            agency = self.agency,
            name = 'main',
            address_1 = 'Road',
            address_2 = '123',
            postal_code = '748562',
            area = 'CENTRAL',
            office_number = '7623542',
            mobile_number = '4371856',
            main_branch = True,
        )
        self.branch.save()

        self.user_owner = accounts.models.User(
            email='user_owner@a.com',
            password='12345678',
            is_online=True,
        )
        self.user_owner.save()
        self.user_owner.groups.set([self.AO])

        self.agency_owner = AgencyOwner(
            user = self.user_owner,
            agency = self.agency,
        )
        self.agency_owner.save()

        self.user_admin = accounts.models.User(
            email='user_admin@a.com',
            password='12345678',
            is_online=True,
        )
        self.user_admin.save()
        self.user_admin.groups.set([self.AA])

        self.agency_employee_admin = AgencyEmployee(
            user = self.user_admin,
            first_name = 'f_name_admin',
            last_name = 'l_name_admin',
            contact_number = '91919191',
            ea_personnel_number = 'EA#1',
            agency = self.agency,
            branch = self.branch,
            role = 'AA',
            deleted = False,
        )
        self.agency_employee_admin.save()

        self.user_manager = accounts.models.User(
            email = 'user_manager@a.com',
            password = '12345678',
            is_online = True,
        )
        self.user_manager.save()
        self.user_manager.groups.set([self.AM])

        self.agency_employee_manager = AgencyEmployee(
            user=self.user_manager,
            first_name = 'f_name_manager',
            last_name = 'l_name_manager',
            contact_number = '92929292',
            ea_personnel_number = 'EA#2',
            agency = self.agency,
            branch = self.branch,
            role = 'AM',
            deleted = False,
        )
        self.agency_employee_manager.save()

        self.user_sales = accounts.models.User(
            email = 'user_sales@a.com',
            password = '12345678',
            is_online = True,
        )
        self.user_sales.save()
        self.user_sales.groups.set([self.AS])

        self.agency_employee_sales = AgencyEmployee(
            user = self.user_sales,
            first_name = 'f_name_sales',
            last_name = 'l_name_sales',
            contact_number = '93939393',
            ea_personnel_number = 'EA#3',
            agency = self.agency,
            branch = self.branch,
            role = 'AS',
            deleted = False,
        )
        self.agency_employee_sales.save()

# Start of tests
class EmployerListViewTestCase(SetUp, TestCase):
    def test_anon_access(self):
        request = self.factory.get(reverse('employer_list_route'))
        request.user = AnonymousUser()
        response = EmployerListView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_potential_employer_access(self):
        request = self.factory.get(reverse('employer_list_route'))
        request.user = self.user_potential_employer
        response = EmployerListView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_owner_access(self):
        request = self.factory.get(reverse('employer_list_route'))
        request.user = self.user_owner
        response = EmployerListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_admin_access(self):
        request = self.factory.get(reverse('employer_list_route'))
        request.user = self.user_admin
        response = EmployerListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_manager_access(self):
        request = self.factory.get(reverse('employer_list_route'))
        request.user = self.user_manager
        response = EmployerListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_sales_access(self):
        request = self.factory.get(reverse('employer_list_route'))
        request.user = self.user_sales
        response = EmployerListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
