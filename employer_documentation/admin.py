from django.contrib import admin
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocSig,
    EmployerDocMaidStatus,
    EmployerPaymentTransaction,
    EmployerDocSponsor,
    EmployerDocJointApplicant,
    JobOrder,
    PdfArchive,
)

# Register your models here.
admin.site.register(Employer)
admin.site.register(EmployerDoc)
admin.site.register(EmployerDocSig)
admin.site.register(EmployerDocMaidStatus)
admin.site.register(EmployerPaymentTransaction)
admin.site.register(EmployerDocSponsor)
admin.site.register(EmployerDocJointApplicant)
admin.site.register(JobOrder)
admin.site.register(PdfArchive)
