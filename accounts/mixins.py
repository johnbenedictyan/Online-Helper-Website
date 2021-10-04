from django.urls import reverse_lazy
from onlinemaid.mixins import GroupRequiredMixin


class PotentialEmployerGrpRequiredMixin(GroupRequiredMixin):
    group_required = u"Employers"
    login_url = reverse_lazy('sign_in')
    permission_denied_message = '''
        You are required to login using an employer's account to perform this
        action
    '''
