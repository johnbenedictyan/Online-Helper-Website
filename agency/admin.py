from django.contrib import admin
from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOpeningHours, AgencyPlan,
    AgencyOwner
)

# Register your models here.
admin.site.register(Agency)
admin.site.register(AgencyEmployee)
admin.site.register(AgencyBranch)
admin.site.register(AgencyOpeningHours)
admin.site.register(AgencyPlan)
admin.site.register(AgencyOwner)