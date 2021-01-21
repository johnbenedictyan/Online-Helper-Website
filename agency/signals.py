# Imports from python

# Imports from django
from django.db.models.signals import post_save
from django.dispatch import receiver

# Imports from other apps

# Imports from within the app
from .models import Agency, AgencyBranch, AgencyOperatingHours, PotentialAgency

# Utiliy Classes and Functions
def agency_completed(agency):
    """ This function will check if the branch_complete and
        operating_hours_complete booleans are True.
        If they are both true then the function will set the agency complete
        field to True.

    Args:
        agency ([obj]): [The agency model object]
    """
    if(
        agency.branch_complete == True and 
        agency.operating_hours_complete == True
    ):
        agency.completed = True
        agency.save()


# Start of Signals
@receiver(post_save, sender=Agency)
def agency_created(sender, instance, created, **kwargs):
    if created == True:
        pa = PotentialAgency.objects.get(
            license_number = instance.license_number
        )
        pa.delete()

@receiver(post_save, sender=AgencyBranch)
def agency_location_completed(sender, instance, created, **kwargs):
    if created == False:
        agency = instance.agency
        branch_values = list(instance.__dict__.values())
        if '' in branch_values:
            branch_valid = False
        else:
            branch_valid = True
        
        if branch_valid == True:
            agency.branch_complete = branch_valid
            agency.save()
        
            if(
                agency.branch_complete == True and 
                agency.operating_hours_complete == True
            ):
                agency.completed = True
                agency.save()

@receiver(post_save, sender=AgencyOperatingHours)
def agency_operating_hours_completed(sender, instance, created, **kwargs):
    if created == False:
        agency = instance.agency
        operating_hours_values = list(instance.__dict__.values())
        
        if '' in operating_hours_values:
            operating_hours_valid = False
        else:
            operating_hours_valid = True
        
        if operating_hours_valid == True:
            agency.operating_hours_complete = operating_hours_valid
            agency.save()
        
            if(
                agency.branch_complete == True and 
                agency.operating_hours_complete == True
            ):
                agency.completed = True
                agency.save()
