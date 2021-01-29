# Imports from python

# Imports from django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Imports from other apps

# Imports from within the app
from .models import (
    Maid, MaidBiodata, MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare,
    MaidDisabledCare, MaidGeneralHousework, MaidCooking, MaidStatus, 
    MaidAgencyFeeTransaction
)

# Utiliy Classes and Functions
def maid_completed(maid):
    if(
        maid.biodata_complete == True and 
        maid.family_details_complete == True and 
        maid.care_complete == True
    ):
        maid.complete = True
        maid.save()

# Start of Signals
@receiver(post_save, sender=MaidBiodata)
def maid_biodata_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        biodata_valid = True

        for k,v in instance.__dict__.items():
            if not v:
                biodata_valid = False

        maid.biodata_complete = biodata_valid
        maid.save()
        if biodata_valid == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidFamilyDetails)
def maid_family_details_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        family_details_valid = True

        for k,v in instance.__dict__.items():
            if not v:
                family_details_valid = False
                if k is 'number_of_children' or k is 'number_of_siblings':
                    if v is 0:
                        family_details_valid = True

        maid.family_details_complete = family_details_valid
        maid.save()
        if family_details_valid == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidInfantChildCare)
@receiver(post_save, sender=MaidElderlyCare)
@receiver(post_save, sender=MaidDisabledCare)
@receiver(post_save, sender=MaidGeneralHousework)
@receiver(post_save, sender=MaidCooking)
def maid_care_completed(sender, instance, created, **kwargs):
    if created == False:
        care_models = [
            MaidInfantChildCare,
            MaidElderlyCare,
            MaidDisabledCare,
            MaidGeneralHousework,
            MaidCooking
        ]
        maid = instance.maid
        care_complete = maid.care_complete

        instance_model_class = instance.__class__
        if instance_model_class in care_models:
            care_models.remove(instance_model_class)
            try:
                for i in care_models:
                    for k,v in i.objects.get(maid=maid).__dict__.items():
                        if k is not 'other_remarks':
                            if not v:
                                raise Exception
            except Exception as e:
                care_complete = False
            else:
                care_complete = True
        
        maid.care_complete = care_complete
        maid.save()
        if care_complete == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidStatus)
def maid_status_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        status_valid = True

        for k,v in instance.__dict__.items():
            if not v:
                status_valid = False
        
        maid.status_complete = status_valid
        maid.save()
        if status_valid == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidAgencyFeeTransaction)
def update_agency_fee(sender, instance, **kwargs):
    maid = instance.maid
    
    transactions = MaidAgencyFeeTransaction.objects.filter(
        maid=maid
    )

    amount = 0
    for transaction in transactions:
        if transaction.transaction_type == 'ADD':
            amount += transaction.amount
        elif transaction.transaction_type == 'SUB':
            amount -= transaction.amount
        
    maid.agency_fee_amount = amount
    maid.save()
