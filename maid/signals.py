# Global Imports
import random

# Django Imports
from django.db.models.signals import post_save
from django.dispatch import receiver

# Project Apps Imports

# Imports from within the app
from .models import (
    Maid, MaidInfantChildCare, MaidElderlyCare, MaidDisabledCare,
    MaidGeneralHousework, MaidCooking, MaidResponsibility
)

# Utiliy Classes and Functions


def maid_main_responsibility(maid):
    care_model_list = [
        MaidInfantChildCare,
        MaidElderlyCare,
        MaidDisabledCare,
        MaidGeneralHousework,
        MaidCooking
    ]

    responsibility_transmap = {
        'MaidInfantChildCare': 'CFI',
        'MaidElderlyCare': 'CFE',
        'MaidDisabledCare': 'CFD',
        'MaidGeneralHousework': 'GEH',
        'MaidCooking': 'COK'
    }

    responsibility_dict = {}

    for i in care_model_list:
        for k, v in i.objects.get(maid=maid).__dict__.items():
            if k == 'assessment':
                responsibility_dict[i.__name__] = v

    main_responsibility_value = max(responsibility_dict.values())
    main_responsibilities = []
    db_responsibilities = [
        i.get_db_value() for i in maid.responsibilities.all()
    ]
    responsibilities_tbd = []

    for k, v in responsibility_dict.items():
        if v == main_responsibility_value:
            main_responsibilities.append(
                responsibility_transmap[k]
            )

    for i in main_responsibilities:
        if i in db_responsibilities:
            main_responsibilities = [i]
        elif len(main_responsibilities) > 1:
            main_responsibilities = [random.choice(main_responsibilities)]

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
