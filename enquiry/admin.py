from django.contrib import admin
from .models import GeneralEnquiry, AgencyEnquiry, MaidEnquiry

# Register your models here.
admin.site.register(GeneralEnquiry)
admin.site.register(AgencyEnquiry)
admin.site.register(MaidEnquiry)