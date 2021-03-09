from django.test import TestCase, RequestFactory
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.files.images import ImageFile
from django.contrib.auth.models import AnonymousUser, Group

import accounts
from onlinemaid.helper_functions import encrypt_string
from agency.models import Agency, AgencyBranch, AgencyOwner, AgencyEmployee, PotentialAgency
from maid.models import Maid
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

        self.potential_agency = PotentialAgency(
            name = 'pa',
            license_number = '12345',
            person_in_charge = 'pa',
            contact_number = '1',
            email = 'a@a.com',
        )
        self.potential_agency.save()
        
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
            first_name = 'admin',
            last_name = 'admin',
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
            first_name = 'manager',
            last_name = 'manager',
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
            first_name = 'sales',
            last_name = 'sales',
            contact_number = '93939393',
            ea_personnel_number = 'EA#3',
            agency = self.agency,
            branch = self.branch,
            role = 'AS',
            deleted = False,
        )
        self.agency_employee_sales.save()

        self.fdw_passport, self.fdw_nonce, self.fdw_tag = encrypt_string(
            'PPT1000001',
            settings.ENCRYPTION_KEY
        )
        self.maid = Maid(
            agency=self.agency,
            name='fdw name',
            reference_number='FDW-01',
            passport_number=self.fdw_passport,
            nonce=self.fdw_nonce,
            tag=self.fdw_tag,
            maid_type='NEW',
            days_off=4,
            passport_status=0,
            remarks='Some remarks',
            skills_evaluation_method='DEC',
            published=True,
            featured=False,
        )
        with open('static/favicon-16x16.png', 'rb') as fp:
            self.maid.photo = ImageFile(fp, 'photo.png')
            self.maid.save()
    
        self.employer_nric, self.employer_nonce, self.employer_tag = encrypt_string(
            'S0000000C',
            settings.ENCRYPTION_KEY
        )
        self.employer_admin = Employer(
            agency_employee = self.agency_employee_admin,
            employer_name = 'employer admin',
            employer_email = 'employer_admin@e.com',
            employer_mobile_number = '83838383',
            employer_nric = self.employer_nric,
            nonce = self.employer_nonce,
            tag = self.employer_tag,
            employer_address_1 = 'The Road',
            employer_address_2 = '123',
            employer_post_code = '098765',
        )
        self.employer_admin.save()

        self.employer_manager = Employer(
            agency_employee = self.agency_employee_manager,
            employer_name = 'employer manager',
            employer_email = 'employer_manager@e.com',
            employer_mobile_number = '84848484',
            employer_nric = self.employer_nric,
            nonce = self.employer_nonce,
            tag = self.employer_tag,
            employer_address_1 = 'The Road',
            employer_address_2 = '123',
            employer_post_code = '098765',
        )
        self.employer_manager.save()

        self.employer_sales = Employer(
            agency_employee = self.agency_employee_sales,
            employer_name = 'employer sales',
            employer_email = 'employer_sales@e.com',
            employer_mobile_number = '85858585',
            employer_nric = self.employer_nric,
            nonce = self.employer_nonce,
            tag = self.employer_tag,
            employer_address_1 = 'The Road',
            employer_address_2 = '123',
            employer_post_code = '098765',
        )
        self.employer_sales.save()

        const_decimal = 100
        const_int = 1
        employer_count = 1
        for employer in [self.employer_admin, self.employer_manager, self.employer_sales]:
            setattr(self, 'employerdoc_' + employer.agency_employee.first_name, EmployerDoc(
                case_ref_no = 'DOC-0' + str(employer_count),
                employer = employer,
                fdw = self.maid,
                monthly_combined_income = 3,
                # spouse_required = False,
                # sponsor_required = False,
                agreement_date = timezone.now(),
                b1_service_fee = const_decimal,
                b2a_work_permit_application_collection = const_decimal,
                b2b_medical_examination_fee = const_decimal,
                b2c_security_bond_accident_insurance = const_decimal,
                b2d_indemnity_policy_reimbursement = const_decimal,
                b2e_home_service = const_decimal,
                b2f_counselling = const_decimal,
                b2g_sip = const_decimal,
                b2h_replacement_months = const_int,
                b2h_replacement_cost = const_decimal,
                b2i_work_permit_renewal = const_decimal,
                b2j1_other_services_description = '1',
                b2j1_other_services_fee = const_decimal,
                b2j2_other_services_description = '2',
                b2j2_other_services_fee = const_decimal,
                b2j3_other_services_description = '3',
                b2j3_other_services_fee = const_decimal,
                ca_deposit = 1500,
                fdw_is_replacement = False,
                # fdw_replaced = ,
                # b4_loan_transferred = ,
                c1_3_handover_days = const_int,
                c3_2_no_replacement_criteria_1 = 'Criteria 1',
                c3_2_no_replacement_criteria_2 = 'Criteria 2',
                c3_2_no_replacement_criteria_3 = 'Criteria 3',
                c3_4_no_replacement_refund = const_decimal,
                c4_1_number_of_replacements = const_int,
                c4_1_replacement_period = const_int,
                c4_1_replacement_after_min_working_days = const_int,
                c4_1_5_replacement_deadline = const_int,
                c5_1_1_deployment_deadline = const_int,
                c5_1_1_failed_deployment_refund = const_decimal,
                c5_1_2_refund_within_days = const_int,
                c5_1_2_before_fdw_arrives_charge = const_decimal,
                c5_1_2_after_fdw_arrives_charge = const_decimal,
                c5_2_2_can_transfer_refund_within = const_int,
                c5_3_2_cannot_transfer_refund_within = const_int,
                c6_4_per_day_food_accommodation_cost = const_decimal,
                c6_6_per_session_counselling_cost = const_decimal,
                c9_1_independent_mediator_1 = 'Mediator 1',
                c9_2_independent_mediator_2 = 'Mediator 2',
                c13_termination_notice = const_int,
                c3_5_fdw_sleeping_arrangement = 'Have own room',
                c4_1_termination_notice = const_int,
                residential_dwelling_type = 'HDB',
                fdw_clean_window_exterior = False,
                # window_exterior_location = ,
                # grilles_installed_require_cleaning = ,
                # adult_supervision = ,
                # received_sip_assessment_checklist = ,
                # verifiy_employer_understands_window_cleaning = ,
            ))
            getattr(self, 'employerdoc_' + employer.agency_employee.first_name).save()
            employer_count += 1
        # print(self.employerdoc_admin.employer.employer_name)
        # print(self.employerdoc_manager.employer.employer_name)
        # print(self.employerdoc_sales.employer.employer_name)

# Start of tests
class EmployerListViewTestCase(SetUp, TestCase):
    ROUTE = 'employer_list_route'

    def setUp(self):
        super().setUp()
        self.request = self.factory.get(reverse(
            self.ROUTE,
            )
        )

    def test_anon_redirect(self):
        self.request.user = AnonymousUser()
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 302)

    def test_potential_employer_redirect(self):
        self.request.user = self.user_potential_employer
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 302)

    def test_owner_access(self):
        self.request.user = self.user_owner
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_admin_access(self):
        self.request.user = self.user_admin
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_manager_access(self):
        self.request.user = self.user_manager
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_sales_access(self):
        self.request.user = self.user_sales
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

class DocListViewTestCase(SetUp, TestCase):
    ROUTE = 'employerdoc_list_route'
    
    def setUp(self):
        super().setUp()
        self.kwargs_ed_admin = {
            'employer_pk': self.employer_admin.pk,
        }
        self.request = self.factory.get(reverse(
            self.ROUTE,
            kwargs=self.kwargs_ed_admin
            )
        )

    def test_anon_redirect(self):
        self.request.user = AnonymousUser()
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 302)

    def test_potential_employer_redirect(self):
        self.request.user = self.user_potential_employer
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 302)

    def test_owner_access(self):
        self.request.user = self.user_owner
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_admin_access(self):
        self.request.user = self.user_admin
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_manager_access(self):
        self.request.user = self.user_manager
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_sales_access(self):
        self.request.user = self.user_sales
        response = EmployerListView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)
