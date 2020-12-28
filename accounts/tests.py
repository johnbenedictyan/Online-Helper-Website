# Imports from the system
import random
import string

# Imports from django
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.crypto import get_random_string

# Imports from foreign installed apps

# Imports from local app
from .forms import EmployerCreationForm, SignInForm, AgencySignInForm
from .models import Employer
from .mixins import VerifiedEmployerMixin

# Start of Tests

## Helper Functions
UserModel = get_user_model()

def r_string(length):
    r_str = ''.join(
        random.choice(string.ascii_lowercase) for i in range(length)
    )
    return r_str

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)

def r_contact_number():
    return random.randint(80000000, 99999999)

def create_test_user():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_user_model().objects.create_user(
        email=f'{r_string(4)}@{r_string(4)}.com',
        password=f'{get_random_string(10, chars)}'
    )

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
        user=new_user,
        first_name=r_string(5),
        last_name=r_string(5),
        contact_number=r_contact_number()
    )
    pe_group = Group.objects.get(
        name='Potential Employers'
    ) 
    pe_group.user_set.add(
        new_user
    )

    return new_pe

class PotentialEmployersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_potential_employer_group()
        cls.pe = create_test_potential_employer()
        
    def testCanCreate(self):
        new_user = create_test_user()
        new_pe = Employer.objects.create(
            user=new_user,
            first_name=r_string(5),
            last_name=r_string(5),
            contact_number=r_contact_number()
        )

        pe_from_db=Employer.objects.get(
            user=new_user
        )
        self.assertEquals(new_pe.first_name,pe_from_db.first_name)
        self.assertEquals(new_pe.last_name,pe_from_db.last_name)
        self.assertEquals(str(new_pe.contact_number),pe_from_db.contact_number)


    def testCanUpdate(self):
        new_first_name = r_string(6)
        new_last_name = r_string(6)
        new_contact_number = r_contact_number()

        Employer.objects.filter(
            pk=self.pe.pk
        ).update(
            first_name=new_first_name,
            last_name=new_last_name,
            contact_number=new_contact_number
        )

        self.pe.refresh_from_db()
        self.assertEquals(self.pe.first_name, new_first_name)
        self.assertEquals(self.pe.last_name, new_last_name)
        self.assertEquals(self.pe.contact_number, str(new_contact_number))

    def testCanDelete(self):
        test_pk = self.pe.pk
        Employer.objects.filter(
            pk=test_pk
        ).delete()
        with self.assertRaises(Employer.DoesNotExist):
            Employer.objects.get(
                pk=test_pk
            )