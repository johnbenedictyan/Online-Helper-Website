from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    EmployerDoc,
    EmployerDocMaidStatus,
    EmployerDocSig,
    JobOrder,
)

@receiver(post_save, sender=EmployerDoc)
def employer_doc_post_save(sender, instance, created, **kwargs):
    if created:
        # If SQL INSERT, create EmployerDocSig, EmployerDocMaidStatus,
        # JobOrder instances.
        EmployerDocSig.objects.create(employer_doc=instance)
        EmployerDocMaidStatus.objects.create(employer_doc=instance)
        JobOrder.objects.create(employer_doc=instance)
    else:
        # If SQL UPDATE, check if EmployerDocSig, EmployerDocMaidStatus,
        # JobOrder instances exist.
        if not hasattr(instance, 'rn_signatures_ed'):
            EmployerDocSig.objects.create(employer_doc=instance)
        if not hasattr(instance, 'rn_maidstatus_ed'):
            EmployerDocMaidStatus.objects.create(employer_doc=instance)
        if not hasattr(instance, 'rn_joborder_ed'):
            JobOrder.objects.create(employer_doc=instance)
        
        # If SQL UPDATE, reset all e-signatures in EmployerDocSig instance
        doc_sig_obj = instance.rn_signatures_ed
        doc_sig_obj.employer_signature = None
        doc_sig_obj.fdw_signature = None
        doc_sig_obj.agency_staff_signature = None
        doc_sig_obj.spouse_signature = None
        doc_sig_obj.sponsor_signature = None
        doc_sig_obj.employer_witness_signature = None
        doc_sig_obj.fdw_witness_signature = None
        doc_sig_obj.agency_staff_witness_signature = None
        doc_sig_obj.save()
