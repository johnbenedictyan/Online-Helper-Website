# Imports from python

# Imports from django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Imports from other apps

# Imports from within the app
from .models import (
    Maid, MaidBiodata, MaidFamilyDetails, MaidInfantChildCare, MaidElderlyCare,
    MaidDisabledCare, MaidGeneralHousework, MaidCooking, MaidStatus
)

# Utiliy Classes and Functions
def maid_completed(maid):
    if(
        maid.biodata_complete == True and 
        maid.family_details_complete == True and 
        maid.infant_child_care_complete == True and 
        maid.elderly_care_complete == True and 
        maid.disabled_care_complete == True and 
        maid.general_housework_complete == True and 
        maid.cooking_complete == True
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
def maid_infant_child_care_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        infant_child_care_valid = True

        for k,v in instance.__dict__.items():
            if k is not 'other_remarks':
                if not v:
                    infant_child_care_valid = False
        
        maid.infant_child_care_complete = infant_child_care_valid
        maid.save()
        if infant_child_care_valid == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidElderlyCare)
def maid_elderly_care_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        elderly_care_valid = True

        for k,v in instance.__dict__.items():
            if k is not 'other_remarks':
                if not v:
                    elderly_care_valid = False
        
        maid.elderly_care_complete = elderly_care_valid
        maid.save()
        if elderly_care_valid == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidDisabledCare)
def maid_disabled_care_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        disabled_care_valid = True

        for k,v in instance.__dict__.items():
            if k is not 'other_remarks':
                if not v:
                    disabled_care_valid = False
    
        maid.disabled_care_complete = disabled_care_valid
        maid.save()
        if disabled_care_valid == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidGeneralHousework)
def maid_general_housework_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        general_housework_valid = True

        for k,v in instance.__dict__.items():
            if k is not 'other_remarks':
                if not v:
                    general_housework_valid = False
        
        maid.general_housework_complete = general_housework_valid
        maid.save()
        if general_housework_valid == True:
            maid_completed(maid)

@receiver(post_save, sender=MaidCooking)
def maid_cooking_completed(sender, instance, created, **kwargs):
    if created == False:
        maid = instance.maid
        cooking_valid = True

        for k,v in instance.__dict__.items():
            if k is not 'other_remarks':
                if not v:
                    cooking_valid = False
        
        maid.cooking_complete = cooking_valid
        maid.save()
        if cooking_valid == True:
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