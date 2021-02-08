from django.contrib.auth import get_user_model
from accounts.models import Employer

def create_employer(backend, user, response, *args, **kwargs):
    """
    Pipeline for social-django to create Employer object for user
    who registers with Google/Facebook
    """
    employer = Employer.objects.filter(user=user).first()
    if employer is None:
        employer = Employer(user=user)

    if backend.name == "facebook":  
        employer.first_name = response.get('first_name')
        employer.last_name = response.get('middle_name') + ' ' + response.get('last_name')
        # Facebook does not expose phone numbers, set contact_number to all 0s.
        employer.contact_number = '0000000000'
    
    elif backend.name == "google-oauth2":
        employer.first_name = response.get('given_name')
        employer.last_name = response.get('family_name')
        # Google OAuth does not expose phone numbers, set contact_number to all 0s.
        employer.contact_number = '0000000000'
    
    employer.save()