from django.test import TestCase, RequestFactory
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.files.images import ImageFile
from django.contrib.auth.models import AnonymousUser, Group

import accounts
from onlinemaid.constants import AG_OWNERS, AG_ADMINS, AG_MANAGERS, AG_SALES, P_EMPLOYERS
from onlinemaid.helper_functions import encrypt_string
from agency.models import Agency, AgencyBranch, AgencyOwner, AgencyEmployee, PotentialAgency
from maid.models import Maid
from .views import *

# Setup class to seed test database with mock data
# Test cases in this app should inherit from this class
class SetUp():
    '''
    Setup class to populate test database with agency, users, etc
    '''
    view_kwargs = {}

    def setUp(self):
        self.factory = RequestFactory()

        group_choices = {
            'AO': AG_OWNERS,
            'AA': AG_ADMINS,
            'AM': AG_MANAGERS,
            'AS': AG_SALES,
            'PE': P_EMPLOYERS,
        }
        for k,v in group_choices.items():
            group_instance = Group(name=v)
            setattr(self, k, group_instance)
            group_instance.save()

        self.user_potential_employer = accounts.models.User(
            email='user_potential_employer@e.com',
            password='12345678',
            is_online=True,
        )
        self.user_potential_employer.save()
        self.user_potential_employer.groups.set([self.PE])

        self.potential_employer = accounts.models.PotentialEmployer(
            user=self.user_potential_employer,
            name='name',
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

        self.branch_1 = AgencyBranch(
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
        self.branch_1.save()

        self.branch_2 = AgencyBranch(
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
        self.branch_2.save()

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
            name = 'admin',
            contact_number = '91919191',
            ea_personnel_number = 'EA#1',
            agency = self.agency,
            branch = self.branch_1,
            role = 'AA',
            deleted = False,
        )
        self.agency_employee_admin.save()

        self.user_manager_b1 = accounts.models.User(
            email = 'user_manager_1@a.com',
            password = '12345678',
            is_online = True,
        )
        self.user_manager_b1.save()
        self.user_manager_b1.groups.set([self.AM])

        self.agency_employee_manager_b1 = AgencyEmployee(
            user=self.user_manager_b1,
            name = 'manager',
            # last_name = '1',
            contact_number = '92929292',
            ea_personnel_number = 'EA#2',
            agency = self.agency,
            branch = self.branch_1,
            role = 'AM',
            deleted = False,
        )
        self.agency_employee_manager_b1.save()

        self.user_manager_b2 = accounts.models.User(
            email = 'user_manager_2@a.com',
            password = '12345678',
            is_online = True,
        )
        self.user_manager_b2.save()
        self.user_manager_b2.groups.set([self.AM])

        self.agency_employee_manager_b2 = AgencyEmployee(
            user=self.user_manager_b2,
            name = 'manager',
            # last_name = '2',
            contact_number = '92929292',
            ea_personnel_number = 'EA#3',
            agency = self.agency,
            branch = self.branch_2,
            role = 'AM',
            deleted = False,
        )
        self.agency_employee_manager_b2.save()

        self.user_sales_b1 = accounts.models.User(
            email = 'user_sales_1@a.com',
            password = '12345678',
            is_online = True,
        )
        self.user_sales_b1.save()
        self.user_sales_b1.groups.set([self.AS])

        self.agency_employee_sales_b1 = AgencyEmployee(
            user = self.user_sales_b1,
            name = 'sales',
            # last_name = '1',
            contact_number = '93939393',
            ea_personnel_number = 'EA#4',
            agency = self.agency,
            branch = self.branch_1,
            role = 'AS',
            deleted = False,
        )
        self.agency_employee_sales_b1.save()

        self.user_sales_b2 = accounts.models.User(
            email = 'user_sales@a.com',
            password = '12345678',
            is_online = True,
        )
        self.user_sales_b2.save()
        self.user_sales_b2.groups.set([self.AS])

        self.agency_employee_sales_b2 = AgencyEmployee(
            user = self.user_sales_b2,
            name = 'sales',
            # last_name = '2',
            contact_number = '93939393',
            ea_personnel_number = 'EA#5',
            agency = self.agency,
            branch = self.branch_1,
            role = 'AS',
            deleted = False,
        )
        self.agency_employee_sales_b2.save()

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
        with open('static/favicon.ico', 'rb') as fp:
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

        self.employer_manager_b1 = Employer(
            agency_employee = self.agency_employee_manager_b1,
            employer_name = 'employer manager 1',
            employer_email = 'employer_manager_1@e.com',
            employer_mobile_number = '84848484',
            employer_nric = self.employer_nric,
            nonce = self.employer_nonce,
            tag = self.employer_tag,
            employer_address_1 = 'The Road',
            employer_address_2 = '123',
            employer_post_code = '098765',
        )
        self.employer_manager_b1.save()

        self.employer_manager_b2 = Employer(
            agency_employee = self.agency_employee_manager_b2,
            employer_name = 'employer manager 2',
            employer_email = 'employer_manager_2@e.com',
            employer_mobile_number = '85858585',
            employer_nric = self.employer_nric,
            nonce = self.employer_nonce,
            tag = self.employer_tag,
            employer_address_1 = 'The Road',
            employer_address_2 = '123',
            employer_post_code = '098765',
        )
        self.employer_manager_b2.save()

        self.employer_sales_b1 = Employer(
            agency_employee = self.agency_employee_sales_b1,
            employer_name = 'employer sales 1',
            employer_email = 'employer_sales_1@e.com',
            employer_mobile_number = '86868686',
            employer_nric = self.employer_nric,
            nonce = self.employer_nonce,
            tag = self.employer_tag,
            employer_address_1 = 'The Road',
            employer_address_2 = '123',
            employer_post_code = '098765',
        )
        self.employer_sales_b1.save()

        self.employer_sales_b2 = Employer(
            agency_employee = self.agency_employee_sales_b2,
            employer_name = 'employer sales 2',
            employer_email = 'employer_sales_2@e.com',
            employer_mobile_number = '87878787',
            employer_nric = self.employer_nric,
            nonce = self.employer_nonce,
            tag = self.employer_tag,
            employer_address_1 = 'The Road',
            employer_address_2 = '123',
            employer_post_code = '098765',
        )
        self.employer_sales_b2.save()

        const_decimal = 100
        const_int = 1
        employer_count = 1
        for employer in [self.employer_admin, self.employer_manager_b1, self.employer_sales_b1,]:
            setattr(self, 'employerdoc_' + employer.agency_employee.name, EmployerDoc(
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
            getattr(self, 'employerdoc_' + employer.agency_employee.name).save()
            employer_count += 1
        # print(self.employerdoc_admin.pk, self.employerdoc_admin.employer.employer_name)
        # print(self.employerdoc_manager.pk, self.employerdoc_manager.employer.employer_name)
        # print(self.employerdoc_sales.pk, self.employerdoc_sales.employer.employer_name)

        # Different agency
        self.potential_agency_other = PotentialAgency(
            name = 'pa',
            license_number = '23456',
            person_in_charge = 'pa',
            contact_number = '1',
            email = 'b@a.com',
        )
        self.potential_agency_other.save()
        
        self.agency_other = Agency(
            company_email = 'b@a.com',
            sales_email = 'b@a.com',
            name = 'BBB Agency Pte Ltd',
            license_number = '23456',
            website_uri = 'https://b.com',
            uen = '87654',
            mission = 'Custom mission',
        )
        self.agency_other.save()

        self.branch_1_other = AgencyBranch(
            agency = self.agency_other,
            name = 'main',
            address_1 = 'Road',
            address_2 = '123',
            postal_code = '748562',
            area = 'CENTRAL',
            office_number = '7623542',
            mobile_number = '4371856',
            main_branch = True,
        )
        self.branch_1_other.save()

        self.user_owner_other = accounts.models.User(
            email='user_owner_other@a.com',
            password='12345678',
            is_online=True,
        )
        self.user_owner_other.save()
        self.user_owner_other.groups.set([self.AO])

        self.agency_owner_other = AgencyOwner(
            user = self.user_owner_other,
            agency = self.agency_other,
        )
        self.agency_owner_other.save()

        self.user_admin_other = accounts.models.User(
            email='user_admin_other@a.com',
            password='12345678',
            is_online=True,
        )
        self.user_admin_other.save()
        self.user_admin_other.groups.set([self.AA])

        self.agency_employee_admin_other = AgencyEmployee(
            user = self.user_admin_other,
            name = 'admin',
            contact_number = '91919191',
            ea_personnel_number = 'EA#1',
            agency = self.agency_other,
            branch = self.branch_1_other,
            role = 'AA',
            deleted = False,
        )
        self.agency_employee_admin_other.save()

        # self.maid_other = Maid(
        #     agency=self.agency_other,
        #     name='fdw name',
        #     reference_number='FDW-01',
        #     passport_number=self.fdw_passport,
        #     nonce=self.fdw_nonce,
        #     tag=self.fdw_tag,
        #     maid_type='NEW',
        #     days_off=4,
        #     passport_status=0,
        #     remarks='Some remarks',
        #     skills_evaluation_method='DEC',
        #     published=True,
        #     featured=False,
        # )
        # with open('static/favicon.ico', 'rb') as fp:
        #     self.maid_other.photo = ImageFile(fp, 'photo.png')
        #     self.maid_other.save()
    
        # self.employer_admin_other = Employer(
        #     agency_employee = self.agency_employee_admin_other,
        #     employer_name = 'employer admin',
        #     employer_email = 'employer_admin@e.com',
        #     employer_mobile_number = '83838383',
        #     employer_nric = self.employer_nric,
        #     nonce = self.employer_nonce,
        #     tag = self.employer_tag,
        #     employer_address_1 = 'The Road',
        #     employer_address_2 = '123',
        #     employer_post_code = '098765',
        # )
        # self.employer_admin_other.save()


# Re-usable tests
def test_anon_redirect(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = AnonymousUser()
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 302)

def test_potential_employer_redirect(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_potential_employer
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 302)

def test_owner_access(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_owner
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 200)

def test_admin_access(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_admin
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 200)

def test_admin_redirect(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_admin_other
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 302)

def test_manager_access(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_manager_b1
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 200)

def test_manager_redirect(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_manager_b2
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 302)

def test_sales_access(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_sales_b1
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 200)

def test_sales_redirect(self, view_and_url_kwargs={}):
    url_kwargs = view_and_url_kwargs.get('url_kwargs', {})
    view_kwargs = view_and_url_kwargs.get('view_kwargs', {})
    self.request = self.factory.get(reverse(
        self.url_route,
        kwargs=url_kwargs,
    ))
    self.request.user = self.user_sales_b2
    response = self.test_view.as_view(**view_kwargs)(self.request, **url_kwargs)
    self.assertEqual(response.status_code, 302)

def gen_view_and_url_kwargs(url_kwargs={}, view_kwargs={}):
    view_and_url_kwargs = {}
    view_and_url_kwargs.update({
        'url_kwargs': url_kwargs,
        'view_kwargs': view_kwargs,
    })
    return view_and_url_kwargs

# Start of tests
class EmployerCreateViewTestCase(SetUp, TestCase):
    url_route = 'employer_create_route'
    test_view = EmployerCreateView

    def test_anon_redirect(self):
        test_anon_redirect(self)

    def test_potential_employer_redirect(self):
        test_potential_employer_redirect(self)

    def test_owner_access(self):
        test_owner_access(self)

    def test_admin_access(self):
        test_admin_access(self)

    def test_manager_access(self):
        test_manager_access(self)

    def test_sales_access(self):
        test_sales_access(self)

class EmployerListViewTestCase(SetUp, TestCase):
    url_route = 'employer_list_route'
    test_view = EmployerListView

    def test_anon_redirect(self):
        test_anon_redirect(self)

    def test_potential_employer_redirect(self):
        test_potential_employer_redirect(self)

    def test_owner_access(self):
        test_owner_access(self)

    def test_admin_access(self):
        test_admin_access(self)

    def test_manager_access(self):
        test_manager_access(self)

    def test_sales_access(self):
        test_sales_access(self)

class StatusListViewTestCase(SetUp, TestCase):
    url_route = 'status_list_route'
    test_view = DocListView

    def test_anon_redirect(self):
        test_anon_redirect(self)

    def test_potential_employer_redirect(self):
        test_potential_employer_redirect(self)

    def test_owner_access(self):
        test_owner_access(self)

    def test_admin_access(self):
        test_admin_access(self)

    def test_manager_access(self):
        test_manager_access(self)

    def test_sales_access(self):
        test_sales_access(self)

class SalesListViewTestCase(SetUp, TestCase):
    url_route = 'sales_list_route'
    test_view = DocListView

    def test_anon_redirect(self):
        test_anon_redirect(self)

    def test_potential_employer_redirect(self):
        test_potential_employer_redirect(self)

    def test_owner_access(self):
        test_owner_access(self)

    def test_admin_access(self):
        test_admin_access(self)

    def test_manager_access(self):
        test_manager_access(self)

    def test_sales_access(self):
        test_sales_access(self)

class EmployerDetailViewTestCase(SetUp, TestCase):
    url_route = 'employer_detail_route'
    test_view = EmployerDetailView
    
    def test_anon_redirect(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_anon_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_potential_employer_redirect(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_potential_employer_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_owner_access(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_owner_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_access_because_same_agency(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_admin_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_redirect_because_not_agency(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_admin_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_admin(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_sales(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_redirect_because_not_branch(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_manager_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_access_because_same_user(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_sales_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_manager(self):
        url_kwargs={
            'employer_pk': self.employer_manager_b1.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_sales(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

class EmployerUpdateViewTestCase(SetUp, TestCase):
    url_route = 'employer_update_route'
    test_view = EmployerUpdateView

    def test_anon_redirect(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_anon_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_potential_employer_redirect(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_potential_employer_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_owner_access(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_owner_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_access_because_same_agency(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_admin_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_redirect_because_not_agency(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_admin_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_admin(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_sales(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_redirect_because_not_branch(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_manager_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_access_because_same_user(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_sales_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_manager(self):
        url_kwargs={
            'employer_pk': self.employer_manager_b1.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_sales(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))
    
class DocListViewTestCase(SetUp, TestCase):
    url_route = 'employerdoc_list_route'
    test_view = EmployerDocListView

    def test_anon_redirect(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_anon_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_potential_employer_redirect(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_potential_employer_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_owner_access(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_owner_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_access_because_same_agency(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_admin_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_redirect_because_not_agency(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_admin_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_admin(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_sales(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_redirect_because_not_branch(self):
        url_kwargs={
            'employer_pk': self.employer_admin.pk,
        }
        test_manager_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_access_because_same_user(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_sales_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_manager(self):
        url_kwargs={
            'employer_pk': self.employer_manager_b1.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_sales(self):
        url_kwargs={
            'employer_pk': self.employer_sales_b1.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

class EmployerDocDetailViewTestCase(SetUp, TestCase):
    url_route = 'employerdoc_detail_route'
    test_view = EmployerDocDetailView
    
    def test_anon_redirect(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
        }
        test_anon_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_potential_employer_redirect(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
        }
        test_potential_employer_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_owner_access(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
        }
        test_owner_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_access_because_same_agency(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
        }
        test_admin_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_redirect_because_not_agency(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
        }
        test_admin_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_admin(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_sales(self):
        url_kwargs={
            'employer_pk': self.employerdoc_sales.employer.pk,
            'employerdoc_pk': self.employerdoc_sales.pk,
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_redirect_because_not_branch(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
        }
        test_manager_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_access_because_same_user(self):
        url_kwargs={
            'employer_pk': self.employerdoc_sales.employer.pk,
            'employerdoc_pk': self.employerdoc_sales.pk,
        }
        test_sales_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_manager(self):
        url_kwargs={
            'employer_pk': self.employerdoc_manager.employer.pk,
            'employerdoc_pk': self.employerdoc_manager.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_sales(self):
        url_kwargs={
            'employer_pk': self.employerdoc_sales.employer.pk,
            'employerdoc_pk': self.employerdoc_sales.pk,
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

# class EmployerDocSigSlugUpdateViewTestCase(SetUp, TestCase):
#     url_route = 'sig_slug_employer_update_route'
#     test_view = EmployerDocSigSlugUpdateView
    
class SignatureUpdateByAgentViewTestCase(SetUp, TestCase):
    url_route = 'signature_employer_update_route'
    test_view = SignatureUpdateByAgentView
    view_kwargs = {
        'model_field_name': 'employer_signature',
        'form_fields': ['employer_signature'],
    }
    
    def test_anon_redirect(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
            'employersubdoc_pk': self.employerdoc_admin.rn_signatures_ed.pk
        }
        test_anon_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_potential_employer_redirect(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
            'employersubdoc_pk': self.employerdoc_admin.rn_signatures_ed.pk
        }
        test_potential_employer_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_owner_access(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
            'employersubdoc_pk': self.employerdoc_admin.rn_signatures_ed.pk
        }
        test_owner_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_access_because_same_agency(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
            'employersubdoc_pk': self.employerdoc_admin.rn_signatures_ed.pk
        }
        test_admin_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_admin_redirect_because_not_agency(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
            'employersubdoc_pk': self.employerdoc_admin.rn_signatures_ed.pk
        }
        test_admin_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_admin(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
            'employersubdoc_pk': self.employerdoc_admin.rn_signatures_ed.pk
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_access_because_same_branch_sales(self):
        url_kwargs={
            'employer_pk': self.employerdoc_sales.employer.pk,
            'employerdoc_pk': self.employerdoc_sales.pk,
            'employersubdoc_pk': self.employerdoc_sales.rn_signatures_ed.pk
        }
        test_manager_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_manager_redirect_because_not_branch(self):
        url_kwargs={
            'employer_pk': self.employerdoc_admin.employer.pk,
            'employerdoc_pk': self.employerdoc_admin.pk,
            'employersubdoc_pk': self.employerdoc_admin.rn_signatures_ed.pk
        }
        test_manager_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_access_because_same_user(self):
        url_kwargs={
            'employer_pk': self.employerdoc_sales.employer.pk,
            'employerdoc_pk': self.employerdoc_sales.pk,
            'employersubdoc_pk': self.employerdoc_sales.rn_signatures_ed.pk
        }
        test_sales_access(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_manager(self):
        url_kwargs={
            'employer_pk': self.employerdoc_manager.employer.pk,
            'employerdoc_pk': self.employerdoc_manager.pk,
            'employersubdoc_pk': self.employerdoc_manager.rn_signatures_ed.pk
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

    def test_sales_redirect_because_not_user_sales(self):
        url_kwargs={
            'employer_pk': self.employerdoc_sales.employer.pk,
            'employerdoc_pk': self.employerdoc_sales.pk,
            'employersubdoc_pk': self.employerdoc_sales.rn_signatures_ed.pk
        }
        test_sales_redirect(self, gen_view_and_url_kwargs(url_kwargs, self.view_kwargs))

