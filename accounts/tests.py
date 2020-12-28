# Imports from the system
import random
import string

# Imports from django
from django.contrib import auth
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse_lazy

# Imports from foreign installed apps
from onlinemaid.helper_functions import (
    r_string, r_contact_number, create_test_user
)

# Imports from local app
from .forms import EmployerCreationForm, SignInForm, AgencySignInForm
from .models import Employer
from .mixins import VerifiedEmployerMixin

# Start of Tests

## Helper Functions
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
        'view_agencyoperatinghours',
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
        first_name=r_string(5),
        last_name=r_string(5),
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
            first_name=r_string(5),
            last_name=r_string(5),
            contact_number=r_contact_number()
        )

        pe_from_db=Employer.objects.get(
            user=new_user['obj']
        )
        self.assertEquals(new_pe.first_name,pe_from_db.first_name)
        self.assertEquals(new_pe.last_name,pe_from_db.last_name)
        self.assertEquals(str(new_pe.contact_number),pe_from_db.contact_number)


    def testCanUpdate(self):
        new_first_name = r_string(6)
        new_last_name = r_string(6)
        new_contact_number = r_contact_number()

        Employer.objects.filter(
            pk=self.pe['obj'].pk
        ).update(
            first_name=new_first_name,
            last_name=new_last_name,
            contact_number=new_contact_number
        )

        self.pe['obj'].refresh_from_db()
        self.assertEquals(self.pe['obj'].first_name, new_first_name)
        self.assertEquals(self.pe['obj'].last_name, new_last_name)
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
    