from django.contrib import admin
from .models import (
    EmployerBase,
    EmployerExtraInfo,
    EmployerDocBase,
    EmployerDocSig,
    EmployerDocJobOrder,
    EmployerDocMaidStatus,
    EmployerDocServiceFeeBase,
    EmployerDocServiceFeeReplacement,
    EmployerDocServiceAgreement,
    EmployerDocEmploymentContract,
    # EmployerDocSalaryPlacementRepayment,
    # EmployerDocRestDayAgreement,
    # EmployerDocHandoverChecklist,
    # EmployerDocTransferConsent,
    # EmployerDocWorkPassAuthorisation,
    # EmployerDocSecurityBondForm,
    # EmployerDocWorkPermitApplicants,
    # EmployerDocIncomeTaxDeclaration,
    # EmployerDocSafetyAgreement,
)

# Register your models here.
admin.site.register(EmployerBase)
admin.site.register(EmployerExtraInfo)
admin.site.register(EmployerDocBase)
admin.site.register(EmployerDocSig)
admin.site.register(EmployerDocJobOrder)
admin.site.register(EmployerDocMaidStatus)
admin.site.register(EmployerDocServiceFeeBase)
admin.site.register(EmployerDocServiceFeeReplacement)
admin.site.register(EmployerDocServiceAgreement)
admin.site.register(EmployerDocEmploymentContract)
# admin.site.register(EmployerDocSalaryPlacementRepayment)
# admin.site.register(EmployerDocRestDayAgreement)
# admin.site.register(EmployerDocHandoverChecklist)
# admin.site.register(EmployerDocTransferConsent)
# admin.site.register(EmployerDocWorkPassAuthorisation)
# admin.site.register(EmployerDocSecurityBondForm)
# admin.site.register(EmployerDocWorkPermitApplicants)
# admin.site.register(EmployerDocIncomeTaxDeclaration)
# admin.site.register(EmployerDocSafetyAgreement)
