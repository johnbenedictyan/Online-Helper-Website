from urllib.parse import quote_plus

from accounts.models import PotentialEmployer
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse

from onlinemaid.constants import EMPLOYERS
# Start of Pipeline


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    # Get the logged in user (if any)
    logged_in_user = strategy.storage.user.get_username(user)

    # Custom: check for email being provided
    if not details.get('email'):
        error = """
            Sorry, but your social network (Facebook or Google) needs to
            provide us your email address.
        """
        return HttpResponseRedirect(
            reverse(
                'repairs-social-network-error'
            ) + "?error=" + quote_plus(error)
        )

    # Custom: if user is already logged in, double check his email matches the
    #         social network email
    if logged_in_user:
        if logged_in_user.lower() != details.get('email').lower():
            error = """
                Sorry, but you are already logged in with another account,
                and the email addresses do not match.
                Try logging out first, please.
            """
            return HttpResponseRedirect(
                reverse(
                    'repairs-social-network-error'
                ) + "?error=" + quote_plus(error)
            )

    return {
        'username': details.get('email').lower(),
    }


def create_employer(backend, user, response, *args, **kwargs):
    """
    Pipeline for social-django to create Employer object for user
    who registers with Google/Facebook
    """
    employer = PotentialEmployer.objects.filter(user=user).first()
    if employer is None:
        potential_employer_obj = PotentialEmployer.objects.create(user=user)
        potential_employer_grp = Group.objects.get(
            name=EMPLOYERS
        )
        potential_employer_grp.user_set.add(user)
        potential_employer_obj.set_employer_relation()
    else:
        return employer
