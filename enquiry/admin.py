from django.contrib import admin
from .models import GeneralEnquiry, ShortlistedEnquiry

# Register your models here.
admin.site.register(GeneralEnquiry)
admin.site.register(ShortlistedEnquiry)