# Django Imports
from django.conf import settings
from django.http import HttpResponseForbidden

# Start of Middlewares


class AdminAccessIPWhiteListMiddleware:
    # Simple Middleware to whitelist IP addresses for admin routes
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_address_list = settings.ADMIN_IP_WHITELIST

    def __call__(self, request):
        # Check whether request starts with '/admin' and
        # if so check whether IP address is in the whitelist.
        if request.path.startswith('/admin') and \
          (not request.META.get('REMOTE_ADDR') in self.ip_address_list):
            return HttpResponseForbidden(
                "You are unauthorized to view this page!"
            )

        response = self.get_response(request)
        return response
