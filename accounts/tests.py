# Imports from the system

# Django Imports
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse_lazy

# Foreign Apps Imports
from onlinemaid.helper_functions import (
    r_string, r_contact_number, create_test_user
)

# Imports from local app
from .forms import EmployerCreationForm
from .models import Employer

# Start of Tests

# Helper Functions


def create_potential_employer_group():
    potential_employers_group, created = Group.objects.get_or_create(
        name='Potential Employers'
    )

    pe_permission_list = [
        'change_employer',
        'delete_employer',
        'view_employer',
        'view_agency',
        'view_agencybranch',
        'view_agencyopeninghours',
        'view_employerbase',
        'view_employerdocbase',
        'view_employerdocemploymentcontract',
        'view_employerdocjoborder',
        'view_employerdocmaidstatus',
        'view_employerdocserviceagreement',
        'view_employerdocservicefeebase',
        'view_employerdocservicefeereplacement',
        'view_employerdocsig',
        'view_employerextrainfo',
        'view_maid',
        'view_maidbiodata',
        'view_maidcooking',
        'view_maiddietaryrestriction',
        'view_maiddisabledcare',
        'view_maidelderlycare',
        'view_maidemploymenthistory',
        'view_maidfamilydetails',
        'view_maidfoodhandlingpreference',
        'view_maidgeneralhousework',
        'view_maidinfantchildcare',
        'view_maidworkduty',
        'view_invoice'
    ]

    for perm in pe_permission_list:
        potential_employers_group.permissions.add(
            Permission.objects.get(
                codename=perm
            )
        )


def create_test_potential_employer():
    new_user = create_test_user()
    new_pe = Employer.objects.create(
        user=new_user['obj'],
        name=r_string(10),
        contact_number=r_contact_number()
    )
    pe_group = Group.objects.get(
        name='Potential Employers'
    )
    pe_group.user_set.add(
        new_user['obj']
    )

    return {
        'email': new_user['email'],
        'password': new_user['password'],
        'obj': new_pe
    }


class PotentialEmployersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_potential_employer_group()
        cls.pe = create_test_potential_employer()

    def testCanCreate(self):
        new_user = create_test_user()
        new_pe = Employer.objects.create(
            user=new_user['obj'],
            name=r_string(10),
            contact_number=r_contact_number()
        )

        pe_from_db = Employer.objects.get(
            user=new_user['obj']
        )
        self.assertEquals(new_pe.name, pe_from_db.name)
        self.assertEquals(
            str(new_pe.contact_number),
            pe_from_db.contact_number
        )

    def testCanUpdate(self):
        new_name = r_string(12)
        new_contact_number = r_contact_number()

        Employer.objects.filter(
            pk=self.pe['obj'].pk
        ).update(
            name=new_name,
            contact_number=new_contact_number
        )

        self.pe['obj'].refresh_from_db()
        self.assertEquals(self.pe['obj'].name, new_name)
        self.assertEquals(
            self.pe['obj'].contact_number, str(new_contact_number)
        )

    def testCanDelete(self):
        test_pk = self.pe['obj'].pk
        Employer.objects.filter(
            pk=test_pk
        ).delete()
        with self.assertRaises(Employer.DoesNotExist):
            Employer.objects.get(
                pk=test_pk
            )


class PotentialEmployersWithoutSignInUrlTest(TestCase):
    def testCanLoadSignInPage(self):
        response = self.client.get(
            reverse_lazy('sign_in')
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/sign-in.html')

    def testCanLoadRegisterPage(self):
        response = self.client.get(
            reverse_lazy('employer_create')
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create/employer-create.html')

    def testWillRedirectToSignInPage(self):
        response = self.client.get(
            reverse_lazy('employer_detail')
        )
        self.assertRedirects(
            response,
            '/accounts/sign-in/employers?next=/accounts/profile/',
            status_code=302,
            target_status_code=200
        )


class PotentialEmployersWithSignInUrlTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_potential_employer_group()
        cls.pe = create_test_potential_employer()

    def testCanLoadProfilePage(self):
        self.client.login(
            email=self.pe['email'],
            password=self.pe['password']
        )
        response = self.client.get(
            reverse_lazy('employer_detail')
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail/employer-detail.html')

    def testCanLogout(self):
        self.client.login(
            email=self.pe['email'],
            password=self.pe['password']
        )
        response = self.client.get(
            reverse_lazy('sign_out')
        )
        self.assertRedirects(
            response,
            reverse_lazy('home'),
            status_code=302,
            target_status_code=200
        )


class PotentialEmployersSignInFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_potential_employer_group()
        cls.pe = create_test_potential_employer()

    def testValidLogin(self):
        test_form_data = {
            'username': self.pe['email'],
            'password': self.pe['password']
        }
        response = self.client.post(
            reverse_lazy('sign_in'),
            test_form_data
        )
        self.assertRedirects(
            response,
            reverse_lazy('home'),
            status_code=302,
            target_status_code=200
        )
        self.assertIn('_auth_user_id', self.client.session)

    def testInvalidLogin(self):
        test_form_data = {
            'username': 'fake@fake.com',
            'password': 'fakepassword'
        }
        response = self.client.post(
            reverse_lazy('sign_in'),
            test_form_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/sign-in.html')
        self.assertNotIn('_auth_user_id', self.client.session)


class PotentialEmployerCreationFormTest(TestCase):
    def ValidEmployerCreationFormSubmission(self):
        test_form_data = {
            'email': 'asd@asd.com',
            'password': 'Password123!',
            'name': 'john doe',
            'contact_number': '81234567'
        }

        test_form = EmployerCreationForm(
            data=test_form_data
        )

        self.assertTrue(test_form.is_valid())

    def testMissingEmailErrorMessage(self):
        test_form_data = {
            'password': 'Password123!',
            'name': 'john doe',
            'contact_number': '81234567'
        }

        test_form = EmployerCreationForm(
            data=test_form_data
        )
        self.assertFalse(
            test_form.is_valid()
        )
        response = self.client.post(
            reverse_lazy('employer_create'),
            test_form_data
        )
        self.assertFormError(
            response,
            'form',
            'email',
            'This field is required.'
        )

    def testMissingFirstNameErrorMessage(self):
        test_form_data = {
            'email': 'asd@asd.com',
            'password': 'Password123!',
            'contact_number': '81234567'
            }

        test_form = EmployerCreationForm(
            data=test_form_data
            )
        self.assertFalse(
            test_form.is_valid()
        )
        response = self.client.post(
            reverse_lazy('employer_create'),
            test_form_data
        )
        self.assertFormError(
            response,
            'form',
            'name',
            'This field is required.'
            )

    def testMissingLastNameErrorMessage(self):
        test_form_data = {
            'email': 'asd@asd.com',
            'password': 'Password123!',
            'name': 'john doe',
            'contact_number': '81234567'
        }

        test_form = EmployerCreationForm(
            data=test_form_data
        )
        self.assertFalse(
            test_form.is_valid()
        )
        response = self.client.post(
            reverse_lazy('employer_create'),
            test_form_data
        )
        self.assertFormError(
            response,
            'form',
            'last_name',
            'This field is required.'
        )

    def testMissingPasswordErrorMessage(self):
        test_form_data = {
            'email': 'asd@asd.com',
            'name': 'john doe',
            'contact_number': '81234567'
        }

        test_form = EmployerCreationForm(
            data=test_form_data
        )
        self.assertFalse(
            test_form.is_valid()
        )
        response = self.client.post(
            reverse_lazy('employer_create'),
            test_form_data
        )
        self.assertFormError(
            response,
            'form',
            'password',
            'This field is required.'
        )

    def testMissingContactNumberErrorMessage(self):
        test_form_data = {
            'email': 'asd@asd.com',
            'password': 'Password123!',
            'name': 'john doe',
        }

        test_form = EmployerCreationForm(
            data=test_form_data
        )
        self.assertFalse(
            test_form.is_valid()
        )
        response = self.client.post(
            reverse_lazy('employer_create'),
            test_form_data
        )
        self.assertFormError(
            response,
            'form',
            'contact_number',
            'This field is required.'
        )
