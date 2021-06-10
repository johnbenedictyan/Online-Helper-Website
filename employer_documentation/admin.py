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
admin.site.register(models.CaseSignature)
admin.site.register(models.CaseStatus)
admin.site.register(models.ArchivedAgencyDetails)
admin.site.register(models.ArchivedMaid)
admin.site.register(models.ArchivedDoc)
# admin.site.register(models.ArchivedEmployerHousehold)
