# Django Imports
from django.contrib import admin

# App Imports
from .models import (
    Agency, AgencyEmployee, AgencyBranch, AgencyOpeningHours, AgencyPlan,
    AgencyOwner
)

# Start of Admin

admin.site.register(Agency)
admin.site.register(AgencyEmployee)
admin.site.register(AgencyBranch)
admin.site.register(AgencyOpeningHours)
admin.site.register(AgencyPlan)
admin.site.register(AgencyOwner)
