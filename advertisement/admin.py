# Register your models here.
from django.contrib import admin

from .models import Advertisement, AdvertisementLocation

admin.site.register(Advertisement)
admin.site.register(AdvertisementLocation)
