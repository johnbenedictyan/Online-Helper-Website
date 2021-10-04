"""onlinemaid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Imports from system
import os


from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


from django_otp.admin import OTPAdminSite


from accounts.urls import urlpatterns as accounts_urls
from advertisement.urls import urlpatterns as advertisement_urls
from agency.urls import urlpatterns as agency_urls
from dashboard.urls import urlpatterns as dashboard_urls
from employer_documentation.urls import urlpatterns as employer_doc_urls
from maid.urls import urlpatterns as maid_urls
from payment.urls import urlpatterns as payment_urls
from shortlist.urls import urlpatterns as shortlist_urls
from website.urls import urlpatterns as website_urls
from enquiry.urls import urlpatterns as enquiry_urls

# Helper Function to populate all of the necessary db fields
USE_DB_PLANTER = os.environ.get('USE_DB_PLANTER') == 'TRUE'
if USE_DB_PLANTER:
    from .helper_functions import (
        populate_necessary_rows, subscription_seed_data
    )
    populate_necessary_rows()
    subscription_seed_data()

# Helper Function to populate some fake maid data
USE_MAID_DB_PLANTER = os.environ.get('USE_MAID_DB_PLANTER') == 'TRUE'
if USE_MAID_DB_PLANTER:
    from .helper_functions import maid_seed_data
    maid_seed_data()

# Django OTP
''' Use this to toggle 2FA on/off '''
USE_2FA = os.environ.get('USE_2FA') == 'TRUE'
if USE_2FA:
    admin.site.__class__ = OTPAdminSite


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(accounts_urls)),
    path('advertisements/', include(advertisement_urls)),
    path('agencies/', include(agency_urls)),
    path('dashboard/', include(dashboard_urls)),
    path('e-d/', include(employer_doc_urls)),
    path('maids/', include(maid_urls)),
    path('payment/', include(payment_urls)),
    path('shortlist/', include(shortlist_urls)),
    path('enquiry/', include(enquiry_urls)),
    path('socia-auth/', include('social_django.urls', namespace='socialauth')),
    path('', include(website_urls))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
