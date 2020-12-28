from django.contrib import admin
from .models import User, Employer, AuditEntry

# Register your models here.
admin.site.register(User)
admin.site.register(Employer)
admin.site.register(AuditEntry)