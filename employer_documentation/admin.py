from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Employer)
admin.site.register(models.EmployerSponsor)
admin.site.register(models.EmployerJointApplicant)
admin.site.register(models.EmployerDoc)
admin.site.register(models.DocServiceFeeSchedule)
admin.site.register(models.DocServAgmtEmpCtr)
admin.site.register(models.DocSafetyAgreement)
admin.site.register(models.DocUpload)
admin.site.register(models.EmployerDocSig)
admin.site.register(models.EmployerDocMaidStatus)
# admin.site.register(models.EmployerPaymentTransaction)
# admin.site.register(models.JobOrder)
admin.site.register(models.PdfArchive)
