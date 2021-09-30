# Django Imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Start of Constants

# General
NO_PREFERENCE = 'ALL'
OTHERS = 'OTH'

# Maid Nationality
MAID_NATIONALITY_CAMBODIAN = 'KHM'
MAID_NATIONALITY_FILIPINO = 'PHL'
MAID_NATIONALITY_INDIAN = 'IND'
MAID_NATIONALITY_INDONESIAN = 'IDN'
MAID_NATIONALITY_MYANMARESE = 'MMR'
MAID_NATIONALITY_SRI_LANKAN = 'LKA'

# Maid Type
MAID_TYPE_NO_EXPERIENCE = 'NEW'
MAID_TYPE_TRANSFER = 'TRA'
MAID_TYPE_SG_EXPERIENCE = 'SGE'
MAID_TYPE_OVERSEAS_EXPERIENCE = 'OVE'

# Property Type
PROPERTY_2_ROOM_HDB = '2RMHDB'
PROPERTY_3_ROOM_HDB = '3RMHDB'
PROPERTY_4_ROOM_HDB = '4RMHDB'
PROPERTY_5_ROOM_HDB = '5RMHDB'
PROPERTY_EXECUTIVE_MAISONETTE_HDB = 'E/MHDB'
PROPERTY_CONDOMINIUM = 'CONDO'
PROPERTY_CONDOMINIUM_PENTHOUSE = 'CONDOP'
PROPERTY_TERRACE = 'TERRACE'
PROPERTY_SEMI_DETACHED = 'SEMI-D'
PROPERTY_BUNGALOW = 'BUNGLO'
PROPERTY_OTHERS = 'OTH'

MAID_NATIONALITY_CHOICES = (
    # (NO_PREFERENCE, _('No preference')),
    (MAID_NATIONALITY_CAMBODIAN, _('Cambodian')),
    (MAID_NATIONALITY_FILIPINO, _('Filipino')),
    (MAID_NATIONALITY_INDIAN, _('Indian')),
    (MAID_NATIONALITY_INDONESIAN, _('Indonesian')),
    (MAID_NATIONALITY_MYANMARESE, _('Myanmarese')),
    (MAID_NATIONALITY_SRI_LANKAN, _('Sri Lankan')),
    # (OTHERS, _('Others'))
)

MAID_TYPE_CHOICES = (
    # (NO_PREFERENCE, _('No preference')),
    (MAID_TYPE_NO_EXPERIENCE, _('No Experience')),
    (MAID_TYPE_TRANSFER, _('Transfer')),
    (MAID_TYPE_SG_EXPERIENCE, _('Singapore Experience')),
    (MAID_TYPE_OVERSEAS_EXPERIENCE, _('Overseas Experience'))
)

PROPERTY_CHOICES = (
    (PROPERTY_2_ROOM_HDB, _('2-Room HDB')),
    (PROPERTY_3_ROOM_HDB, _('3-Room HDB')),
    (PROPERTY_4_ROOM_HDB, _('4-Room HDB')),
    (PROPERTY_5_ROOM_HDB, _('5-Room HDB')),
    (PROPERTY_EXECUTIVE_MAISONETTE_HDB, _('Executive/Maisonette HDB')),
    (PROPERTY_CONDOMINIUM, _('Condominium')),
    (PROPERTY_CONDOMINIUM_PENTHOUSE, _('Condominium Penthouse')),
    (PROPERTY_TERRACE, _('Terrace')),
    (PROPERTY_SEMI_DETACHED, _('Semi-Detached')),
    (PROPERTY_BUNGALOW, _('Bungalow')),
    (PROPERTY_OTHERS, _('Others')),
)


class EnquiryStatusChoices(models.TextChoices):
    OPEN = 'O', _("Open")
    ACCEPTED = 'A', _("Accepted")
    REJECTED = 'R', _("Rejected")
    CLOSED = 'C', _("Closed")
