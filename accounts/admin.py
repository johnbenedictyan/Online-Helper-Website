from django.contrib import admin
from .models import User, PotentialEmployer, AuditEntry

# Register your models here.
admin.site.register(User)
admin.site.register(PotentialEmployer)
admin.site.register(AuditEntry)
