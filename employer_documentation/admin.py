from django.contrib import admin
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocSig,
    EmployerDocMaidStatus,
)

# Register your models here.
admin.site.register(Employer)
admin.site.register(EmployerDoc)
admin.site.register(EmployerDocSig)
admin.site.register(EmployerDocMaidStatus)
