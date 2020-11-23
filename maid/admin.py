from django.contrib import admin
from .models import (
    Maid, MaidWorkDuty, MaidFoodHandlingPreference, MaidDietaryRestriction,
    MaidEmploymentHistory, MaidBiodata, MaidStatus, MaidFamilyDetails,
    MaidInfantChildCare, MaidElderlyCare, MaidDisabledCare, 
    MaidGeneralHousework, MaidCooking
)

# Register your models here.
admin.site.register(Maid)
admin.site.register(MaidWorkDuty)
admin.site.register(MaidFoodHandlingPreference)
admin.site.register(MaidDietaryRestriction)
admin.site.register(MaidEmploymentHistory)
admin.site.register(MaidBiodata)
admin.site.register(MaidStatus)
admin.site.register(MaidFamilyDetails)
admin.site.register(MaidInfantChildCare)
admin.site.register(MaidElderlyCare)
admin.site.register(MaidDisabledCare)
admin.site.register(MaidGeneralHousework)
admin.site.register(MaidCooking)