from django.contrib import admin
from .models import (
    Maid, MaidFoodHandlingPreference, MaidDietaryRestriction, MaidEmploymentHistory,
    MaidInfantChildCare, MaidElderlyCare, MaidDisabledCare, MaidGeneralHousework, MaidCooking,
    MaidResponsibility, MaidLoanTransaction, MaidLanguage
)

# Register your models here.
admin.site.register(Maid)
admin.site.register(MaidFoodHandlingPreference)
admin.site.register(MaidDietaryRestriction)
admin.site.register(MaidEmploymentHistory)
admin.site.register(MaidInfantChildCare)
admin.site.register(MaidElderlyCare)
admin.site.register(MaidDisabledCare)
admin.site.register(MaidGeneralHousework)
admin.site.register(MaidCooking)
admin.site.register(MaidResponsibility)
admin.site.register(MaidLoanTransaction)
admin.site.register(MaidLanguage)