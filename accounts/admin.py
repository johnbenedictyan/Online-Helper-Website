from django.contrib import admin

from .models import AuditEntry, FDWAccount, PotentialEmployer, User

# Register your models here.
admin.site.register(User)
admin.site.register(PotentialEmployer)
admin.site.register(AuditEntry)
admin.site.register(FDWAccount)
