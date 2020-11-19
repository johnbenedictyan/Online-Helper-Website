# Imports from python

# Imports from django
from django.contrib.auth.mixins import AccessMixin

# Imports from other apps

# Imports from within the app

# Utiliy Classes and Functions

# Start of Mixins

class SuperUserRequiredMixin(AccessMixin):
    permission_denied_message = '''You are required to login as a member of 
                                Online Maid Pte Ltd to perform this action'''

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

