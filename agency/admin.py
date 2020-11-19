from django.contrib import admin
from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOperatingHours, AgencyPlan,
    AgencyManager, AgencyOwner
)

# Register your models here.
admin.site.register(Agency)
admin.site.register(AgencyEmployee)
admin.site.register(AgencyBranch)
admin.site.register(AgencyOperatingHours)
admin.site.register(AgencyPlan)
admin.site.register(AgencyManager)
admin.site.register(AgencyOwner)