from django.contrib import admin
from .models import (
    Employer,
    EmployerDoc,
    EmployerDocSig,
    EmployerDocMaidStatus,
    EmployerPaymentTransaction,
    EmployerSponsor,
    EmployerJointApplicant,
    JobOrder,
    PdfArchive,
)

# Register your models here.
admin.site.register(Employer)
admin.site.register(EmployerDoc)
admin.site.register(EmployerDocSig)
admin.site.register(EmployerDocMaidStatus)
admin.site.register(EmployerPaymentTransaction)
admin.site.register(EmployerSponsor)
admin.site.register(EmployerJointApplicant)
admin.site.register(JobOrder)
admin.site.register(PdfArchive)
