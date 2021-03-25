# Imports from python

# Imports from django
from django.utils.translation import ugettext_lazy as _

# Imports from other apps

# Imports from within the app

# Utiliy Classes and Functions

# Start of Constants

# Settings

## General
NO_PREFERENCE = 'ALL'
OTHERS        = 'OTH'

## Maid Age
MAID_AGE_23_TO_29 = '23-29'
MAID_AGE_30_TO_39 = '30-39'
MAID_AGE_40_TO_49 = '40-49'
MAID_AGE_ABOVE_50 = 'above 50'

## Maid Nationality
MAID_NATIONALITY_CAMBODIAN  = 'KHM'
MAID_NATIONALITY_FILIPINO   = 'PHL'
MAID_NATIONALITY_INDIAN     = 'IND'
MAID_NATIONALITY_INDONESIAN = 'IDN'
MAID_NATIONALITY_MYANMARESE = 'MMR'
MAID_NATIONALITY_SRI_LANKAN = 'LKA'

## Maid Rest Days
MAID_REST_DAY_0 = '0RD'
MAID_REST_DAY_1 = '1RD'
MAID_REST_DAY_2 = '2RD'
MAID_REST_DAY_3 = '3RD'
MAID_REST_DAY_4 = '4RD'

## Maid Type
MAID_TYPE_NO_EXPERIENCE       = 'NEW'
MAID_TYPE_TRANSFER            = 'TRA'
MAID_TYPE_SG_EXPERIENCE       = 'SGE'
MAID_TYPE_OVERSEAS_EXPERIENCE = 'OVE'

## Property Type
PROPERTY_2_ROOM_HDB               = '2RMHDB'
PROPERTY_3_ROOM_HDB               = '3RMHDB'
PROPERTY_4_ROOM_HDB               = '4RMHDB'
PROPERTY_5_ROOM_HDB               = '5RMHDB'
PROPERTY_EXECUTIVE_MAISONETTE_HDB = 'E/MHDB'
PROPERTY_CONDOMINIUM              = 'CONDO'
PROPERTY_CONDOMINIUM_PENTHOUSE    = 'CONDOP'
PROPERTY_TERRACE                  = 'TERRACE'
PROPERTY_SEMI_DETACHED            = 'SEMI-D'
PROPERTY_BUNGALOW                 = 'BUNGLO'
PROPERTY_OTHERS                   = 'OTH'

## Mode of Contact
MOBILE_MODE = 'MOBILE'
EMAIL_MODE  = 'EMAIL'

MAID_NATIONALITY_CHOICES = (
    (NO_PREFERENCE, _('No preference')),
    (MAID_NATIONALITY_CAMBODIAN, _('Cambodian')),
    (MAID_NATIONALITY_FILIPINO, _('Filipino')),
    (MAID_NATIONALITY_INDIAN, _('Indian')),
    (MAID_NATIONALITY_INDONESIAN, _('Indonesian')),
    (MAID_NATIONALITY_MYANMARESE, _('Myanmarese')),
    (MAID_NATIONALITY_SRI_LANKAN, _('Sri Lankan')),
    (OTHERS, _('Others'))
)

MAID_TYPE_CHOICES = (
    (NO_PREFERENCE, _('No preference')),
    (MAID_TYPE_NO_EXPERIENCE, _('No Experience')),
    (MAID_TYPE_TRANSFER, _('Transfer')),
    (MAID_TYPE_SG_EXPERIENCE, _('Singapore Experience')),
    (MAID_TYPE_OVERSEAS_EXPERIENCE, _('Overseas Experience'))
)

MAID_AGE_CHOICES = (
    (MAID_AGE_23_TO_29, _('23-29')),
    (MAID_AGE_30_TO_39, _('30-39')),
    (MAID_AGE_40_TO_49, _('40-49')),
    (MAID_AGE_ABOVE_50, _('Above 50'))
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
MAID_REST_DAY_CHOICES = (
    (MAID_REST_DAY_0, _('0 Rest Days Per Month')),
    (MAID_REST_DAY_1, _('1 Rest Days Per Month')),
    (MAID_REST_DAY_2, _('2 Rest Days Per Month')),
    (MAID_REST_DAY_3, _('3 Rest Days Per Month')),
    (MAID_REST_DAY_4, _('4 Rest Days Per Month'))
)
MODE_OF_CONTACT_CHOICES = (
    (MOBILE_MODE, _('Via Mobile')),
    (EMAIL_MODE, _('Via Email'))
)