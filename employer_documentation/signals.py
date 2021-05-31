# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from . import models

# @receiver(post_save, sender=models.EmployerDoc)
# def employer_doc_post_save(sender, instance, created, **kwargs):
#     if created:
#         # If SQL INSERT, create ... instances.
#         pass
#         # models.EmployerDocSig.objects.create(employer_doc=instance)
#         # models.EmployerDocMaidStatus.objects.create(employer_doc=instance)
#         # models.PdfArchive.objects.create(employer_doc=instance)
#     else:
#         # If SQL UPDATE, create ... instances if they don't exist.
#         pass
#         # if not hasattr(instance, 'rn_signatures_ed'):
#         #     models.EmployerDocSig.objects.create(employer_doc=instance)
#         # if not hasattr(instance, 'rn_maidstatus_ed'):
#         #     models.EmployerDocMaidStatus.objects.create(employer_doc=instance)
        
#         # If SQL UPDATE, reset all e-signatures in models.EmployerDocSig instance
#         # doc_sig_obj = instance.rn_signatures_ed
#         # doc_sig_obj.employer_signature = None
#         # doc_sig_obj.fdw_signature = None
#         # doc_sig_obj.agency_staff_signature = None
#         # doc_sig_obj.spouse_signature = None
#         # doc_sig_obj.sponsor_signature = None
#         # doc_sig_obj.employer_witness_signature = None
#         # doc_sig_obj.fdw_witness_signature = None
#         # doc_sig_obj.agency_staff_witness_signature = None
#         # doc_sig_obj.save()
