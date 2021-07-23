# Django Imports
from django.urls import reverse_lazy

# Project Apps Imports
from onlinemaid.mixins import GroupRequiredMixin

# Start of Mixins


class PotentialEmployerGrpRequiredMixin(GroupRequiredMixin):
    group_required = u"Potential Employers"
    login_url = reverse_lazy('sign_in')
    permission_denied_message = '''
        You are required to login using an employer's account to perform this
        action
    '''
