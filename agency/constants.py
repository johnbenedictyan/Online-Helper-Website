# Imports from python

# Imports from django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Imports from other apps

# Imports from within the app

# Utiliy Classes and Functions

# Start of Constants

class AreaChoices(models.TextChoices):
    CENTRAL = 'C', _('Central')
    NORTH = 'N', _('North')
    NORTH_EAST = 'NE', _('North East')
    EAST = 'E', _('East')
    WEST = 'W', _('West')

class AgencyEmployeeRoleChoices(models.TextChoices):
    ADMINISTRATOR = 'AD', _('Administrator')
    MANAGER = 'MA', _('Manager')
    SALES_STAFF = 'SS', _('Sales Staff')
    ADMIN_STAFF = 'AM', _('Admin Staff (No EA Personnel Number)')

class OpeningHoursTypeChoices(models.TextChoices):
    OPENING_HOURS = 'OH', _('Opening Hours')
    APPOINTMENT_ONLY = 'AO', _('Appointment Only')

class OpeningHoursChoices(models.TextChoices):
    TIME0000 = '00:00 AM', _('00:00 AM')
    TIME0030 = '00:30 AM', _('00:30 AM')
    TIME0100 = '01:00 AM', _('01:00 AM') 
    TIME0130 = '01:30 AM', _('01:30 AM') 
    TIME0200 = '02:00 AM', _('02:00 AM') 
    TIME0230 = '02:30 AM', _('02:30 AM') 
    TIME0300 = '03:00 AM', _('03:00 AM') 
    TIME0330 = '03:30 AM', _('03:30 AM') 
    TIME0400 = '04:00 AM', _('04:00 AM') 
    TIME0430 = '04:30 AM', _('04:30 AM') 
    TIME0500 = '05:00 AM', _('05:00 AM') 
    TIME0530 = '05:30 AM', _('05:30 AM') 
    TIME0600 = '06:00 AM', _('06:00 AM') 
    TIME0630 = '06:30 AM', _('06:30 AM') 
    TIME0700 = '07:00 AM', _('07:00 AM') 
    TIME0730 = '07:30 AM', _('07:30 AM') 
    TIME0800 = '08:00 AM', _('08:00 AM') 
    TIME0830 = '08:30 AM', _('08:30 AM') 
    TIME0900 = '09:00 AM', _('09:00 AM') 
    TIME0930 = '09:30 AM', _('09:30 AM')
    TIME1000 = '10:30 AM', _('10:30 AM')
    TIME1030 = '10:00 AM', _('10:00 AM')
    TIME1100 = '11:00 AM', _('11:00 AM')
    TIME1130 = '11:30 AM', _('11:30 AM')
    TIME1200 = '12:00 PM', _('12:00 PM')
    TIME1230 = '12:30 PM', _('12:30 PM')
    TIME1300 = '01:00 PM', _('01:00 PM')
    TIME1330 = '01:30 PM', _('01:30 PM')
    TIME1400 = '02:00 PM', _('02:00 PM')
    TIME1430 = '02:30 PM', _('02:30 PM')
    TIME1500 = '03:00 PM', _('03:00 PM')
    TIME1530 = '03:30 PM', _('03:30 PM')
    TIME1600 = '04:00 PM', _('04:00 PM')
    TIME1630 = '04:30 PM', _('04:30 PM')
    TIME1700 = '05:00 PM', _('05:00 PM')
    TIME1730 = '05:30 PM', _('05:30 PM')
    TIME1800 = '06:00 PM', _('06:00 PM')
    TIME1830 = '06:30 PM', _('06:30 PM')
    TIME1900 = '07:00 PM', _('07:00 PM')
    TIME1930 = '07:30 PM', _('07:30 PM')
    TIME2000 = '08:00 PM', _('08:00 PM')
    TIME2030 = '08:30 PM', _('08:30 PM')
    TIME2100 = '09:00 PM', _('09:00 PM')
    TIME2130 = '09:30 PM', _('09:30 PM')
    TIME2200 = '10:00 PM', _('10:00 PM')
    TIME2230 = '10:30 PM', _('10:30 PM')
    TIME2300 = '11:00 PM', _('11:00 PM')
    TIME2330 = '11:30 PM', _('11:30 PM')