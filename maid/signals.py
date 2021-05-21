# Imports from python
import random

# Imports from django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Imports from other apps

# Imports from within the app
from .constants import MaidResponsibilityChoices

from .models import (
    Maid, MaidInfantChildCare, 
    MaidElderlyCare, MaidDisabledCare, MaidGeneralHousework, MaidCooking, 
    MaidEmploymentStatus, MaidLoanTransaction, MaidResponsibility, 
)

# Utiliy Classes and Functions
def maid_main_responsibility(maid):
    care_models = [
        MaidInfantChildCare,
        MaidElderlyCare,
        MaidDisabledCare,
        MaidGeneralHousework,
        MaidCooking
    ]

    maid_responsibility_translation_table = {
        'MaidInfantChildCare': 'CFI',
        'MaidElderlyCare': 'CFE',
        'MaidDisabledCare': 'CFD',
        'MaidGeneralHousework': 'GEH',
        'MaidCooking': 'COK'
    }

    responsibility_dict = {}

    for i in care_models:
        for k,v in i.objects.get(maid=maid).__dict__.items():
            if k == 'assessment':
                responsibility_dict[i.__name__] = v

    main_responsibility_value = max(responsibility_dict.values())
    main_responsibilities = []
    db_responsibilities = [
        i.get_db_value() for i in maid.responsibilities.all()
    ]
    responsibilities_tbd = []

    for k,v in responsibility_dict.items():
        if v == main_responsibility_value:
            main_responsibilities.append(
                maid_responsibility_translation_table[k]
            )

    for i in main_responsibilities:
        if i in db_responsibilities:
            main_responsibilities = [i]
        elif len(main_responsibilities) > 1:
            main_responsibilities = [random.choice(main_responsibilities)]
    
    if maid.other_care.care_for_pets == True:
        main_responsibilities.append(
            MaidResponsibilityChoices.MAID_RESP_CARE_FOR_PETS
        )
    
    if maid.other_care.gardening == True:
        main_responsibilities.append(
            MaidResponsibilityChoices.MAID_RESP_GARDENING
        )

    for i in db_responsibilities:
        if i not in main_responsibilities:
            responsibilities_tbd.append(i)
        else:
            main_responsibilities.remove(i)

    for i in responsibilities_tbd:
        maid.responsibilities.remove(
            MaidResponsibility.objects.get(
                name=i
            )
        )
    
    for i in main_responsibilities:
        maid.responsibilities.add(
            MaidResponsibility.objects.get(
                name=i
            )
        )

# def maid_completed(maid):
#     if(
#         maid.biodata_complete == True and 
#         maid.family_details_complete == True and 
#         maid.care_complete == True
#     ):
#         maid.complete = True
#         maid.save()

# Start of Signals
@receiver(post_save, sender=Maid)
def maid_counter(sender, instance, created, **kwargs):
    agency = instance.agency
    agency.amount_of_biodata = Maid.objects.filter(
        agency=agency
    ).count()
    agency.amount_of_featured_biodata = Maid.objects.filter(
        agency=agency,
        status='FEAT'
    ).count()
    agency.save()
    
# @receiver(post_save, sender=MaidInfantChildCare)
# @receiver(post_save, sender=MaidElderlyCare)
# @receiver(post_save, sender=MaidDisabledCare)
# @receiver(post_save, sender=MaidGeneralHousework)
# @receiver(post_save, sender=MaidCooking)
# def maid_care_completed(sender, instance, created, **kwargs):
#     care_models = [
#         MaidInfantChildCare,
#         MaidElderlyCare,
#         MaidDisabledCare,
#         MaidGeneralHousework,
#         MaidCooking,
#     ]

#     related_names = {
#         'MaidInfantChildCare': 'infant_child_care',
#         'MaidElderlyCare': 'elderly_care',
#         'MaidDisabledCare': 'disabled_care',
#         'MaidGeneralHousework': 'general_housework',
#         'MaidCooking': 'cooking',
#     }
    
#     maid = instance.maid
#     safe_flag = True

#     for i in care_models:
#         if hasattr(maid, related_names[i.__name__]) == False:
#             safe_flag = False
        
#     care_complete = maid.care_complete
#     instance_model_class = instance.__class__

#     if safe_flag == True:
#         if instance_model_class in care_models:
#             care_models.remove(instance_model_class)
#             try:
#                 for i in care_models:
#                     for k,v in i.objects.get(maid=maid).__dict__.items():
#                         if k != 'other_remarks':
#                             if not v:
#                                 raise Exception
#             except Exception as e:
#                 care_complete = False
#             else:
#                 care_complete = True
        
#         maid.care_complete = care_complete
#         maid.save()
#         if care_complete == True:
#             maid_main_responsibility(maid)
            # maid_completed(maid)

@receiver(post_save, sender=MaidEmploymentStatus)
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

# @receiver(post_save, sender=MaidLoanTransaction)
# def update_agency_fee(sender, instance, **kwargs):
#     maid = instance.maid
    
#     transactions = MaidLoanTransaction.objects.filter(
#         maid=maid
#     )

#     amount = 0
#     for transaction in transactions:
#         if transaction.transaction_type == 'ADD':
#             amount += transaction.amount
#         elif transaction.transaction_type == 'SUB':
#             amount -= transaction.amount
    
#     financial_details = MaidFinancialDetails.objects.get(
#         maid=maid
#     )
#     financial_details.main_loan = amount
#     financial_details.save()
