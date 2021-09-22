# Django Imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Start of Constants
CARE_OWN_COUNTRY = 'OC', _('Experience in own country')
CARE_OVERSEAS = 'OV', _('Experience in overseas')
CARE_SINGAPORE = 'SG', _('Experience in Singapore')
CARE_OWN_COUNTRY_SINGAPORE = 'OC_SG', _(
    'Experience in own country and Singapore'
)
CARE_OWN_COUNTRY_OVERSEAS = 'OC_O', _('Experience in own country and overseas')
CARE_OWN_COUNTRY_OVERSEAS_SINGPAPORE = 'OC_O_SG', _(
    'Experience in own country, overseas and Singapore'
)
CARE_NO_EXP = 'NE', _('No experience, but willing to learn')
CARE_OTHERS = 'OTH', _('Other remarks (Please specify)')


class MaidCountryOfOrigin(models.TextChoices):
    BANGLADESH = 'BGD', _('Bangladesh')
    CAMBODIA = 'KHM', _('Cambodia')
    INDIA = 'IND', _('India')
    INDONESIA = 'IDN', _('Indonesia')
    MYANMAR = 'MMR', _('Myanmar')
    PHILIPPINES = 'PHL', _('Philippines (the)')
    SRI_LANKA = 'LKA', _('Sri Lanka')
    THAILAND = 'THA', _('Thailand')


COUNTRY_LANGUAGE_MAP = {
    MaidCountryOfOrigin.BANGLADESH: 'TAM',
    MaidCountryOfOrigin.CAMBODIA: 'KHM',
    MaidCountryOfOrigin.INDIA: 'TAM',
    MaidCountryOfOrigin.INDONESIA: 'IDN',
    MaidCountryOfOrigin.MYANMAR: 'BUR',
    MaidCountryOfOrigin.PHILIPPINES: 'TAG',
    MaidCountryOfOrigin.SRI_LANKA: 'SIN',
}


class MaidNationalityChoices(models.TextChoices):
    BANGLADESH = 'BGD', _('Bangladeshi')
    CAMBODIA = 'KHM', _('Cambodian')
    INDIA = 'IND', _('Indian')
    INDONESIA = 'IDN', _('Indonesian')
    MYANMAR = 'MMR', _('Myanmar')
    PHILIPPINES = 'PHL', _('Filipino')
    SRI_LANKA = 'LKA', _('Sri Lankan')
    OTHERS = 'OTH', _('Others')


class MaidLanguageChoices(models.TextChoices):
    ENGLISH = 'ENG', _('English')
    MANDARIN = 'MAN', _('Mandarin')
    CHINESE_DIALECT = 'CHD', _('Chinese Dialect')
    MALAY = 'MAL', _('Malay / Bahasa Indonesia')
    HINDI_TAMIL = 'H_T', _('Hindi / Tamil')


class MaidReligionChoices(models.TextChoices):
    BUDDHIST = 'B', _('Buddhist')
    MUSLIM = 'M', _('Muslim')
    HINDU = 'H', _('Hindu')
    CHRISTIAN = 'CH', _('Christain')
    CATHOLIC = 'CA', _('Catholic')
    SIKH = 'S', _('Sikh')
    OTHERS = 'OTH', _('Others')
    NONE = 'NONE', _('None')


class MaidAssessmentChoices(models.IntegerChoices):
    POOR = 1, _('1 - Poor')
    FAIR = 2, _('2 - Fair')
    AVERAGE = 3, _('3 - Average')
    GOOD = 4, _('4 - Good')
    EXCELLENT = 5, _('5 - Excellent')


class MaidResponsibilityChoices(models.TextChoices):
    MAID_RESP_GENERAL_HOUSEWORK = 'GEH', _('General Housework')
    MAID_RESP_COOKING = 'COK', _('Cooking')
    MAID_RESP_CARE_FOR_INFANTS_CHILDREN = 'CFI', _('Care for Infants/Children')
    MAID_RESP_CARE_FOR_ELDERLY = 'CFE', _('Care for the Elderly')
    MAID_RESP_CARE_FOR_DISABLED = 'CFD', _('Care for the Disabled')


class MaidGeneralHouseworkRemarksChoices(models.TextChoices):
    CAN_DO_ALL_HOUSEWORK = 'CAN', _('Able to do all general housework')
    OTHERS = 'OTH', _('Other remarks (Please specify)')


class TypeOfMaidChoices(models.TextChoices):
    NEW = 'NEW', _('No Experience')
    TRANSFER = 'TRF', _('Transfer')
    SINGAPORE_EXPERIENCE = 'SGE', _('Singapore Experience')
    OVERSEAS_EXPERIENCE = 'OVE', _('Overseas Experience')


class MaidPassportStatusChoices(models.IntegerChoices):
    NOT_READY = 0, _('Not Ready')
    READY = 1, _('Ready')


class MaidEducationLevelChoices(models.TextChoices):
    HIGH_SCHOOL = 'HS', _('High School')
    COLLEGE = 'COL', _('College')
    OTHERS = 'OTH', _('Others')


class MaidCreatedOnChoices(models.IntegerChoices):
    THREE_DAYS = 3, _('Last 3 days')
    SEVEN_DAYS = 7, _('Last 7 days')
    FIFTEEN_DAYS = 15, _('Last 15 days')


class MaidLoanDescriptionChoices(models.TextChoices):
    INITIAL_LOAN = 'IML', _('Initial Maid Loan')
    TRANSFER_FEE = 'ATF', _('Add Transfer Fee')
    OTHER_COST = 'AOC', _('Add Other Cost')
    LOAN_REPAYMENT = 'LR', _('Loan Repayment')


class MaidStatusChoices(models.TextChoices):
    UNPUBLISHED = 'UNPUB', _('Unpublished')
    PUBLISHED = 'PUB', _('Published')
    FEATURED = 'FEAT', _('Featured')
    EMPLOYED = 'EMPLOY', _('Employed')


class MaidFoodPreferenceChoices(models.TextChoices):
    PORK = 'P', _('No pork')
    BEEF = 'B', _('No beef')
    VEG = 'V', _('Vegetarian')


class MaidDietaryRestrictionChoices(models.TextChoices):
    PORK = 'P', _('No pork')
    BEEF = 'B', _('No beef')
    VEG = 'V', _('Able to work in a Vegetarian family')


class MaidLanguageProficiencyChoices(models.TextChoices):
    UNABLE = 'UNABLE', _('Unable to speak this language')
    BASIC = 'BASIC', _('Basic')
    INTERMEDIATE = 'INTER', _('Intermediate')
    ADVANCED = 'ADVAN', _('Advanced')


class MaidExperienceChoices(models.TextChoices):
    NO = 'NO', _('No Experience')
    ONE = 'ONE', _('1 Year')
    TWO = 'TWO', _('2 Years')
    THREE = 'THREE', _('3 Years')
    FOUR = 'FOUR', _('4 Years')
    O_FIVE = 'O_FIVE', _('>5 Years')


class MaidEmploymentCountry(models.TextChoices):
    # https://en.wikipedia.org/wiki/ISO_3166-1
    SINGAPORE = 'SGP', _('Singapore')
    HONG_KONG = 'HKG', _('Hong Kong')
    MALAYSIA = 'MYS', _('Malaysia')


class InfantChildCareRemarksChoices(models.TextChoices):
    OWN_COUNTRY = CARE_OWN_COUNTRY
    OVERSEAS = CARE_OVERSEAS
    SINGAPORE = CARE_SINGAPORE
    OWN_COUNTRY_SINGAPORE = CARE_OWN_COUNTRY_SINGAPORE
    OWN_COUNTRY_OVERSEAS = CARE_OWN_COUNTRY_OVERSEAS
    OWN_COUNTRY_OVERSEAS_SINGPAPORE = CARE_OWN_COUNTRY_OVERSEAS_SINGPAPORE
    NO_EXP = CARE_NO_EXP
    NOT_WILLING = 'NW', _('Not willing to care for infants/children')
    OTHERS = CARE_OTHERS


class ElderlyCareRemarksChoices(models.TextChoices):
    OWN_COUNTRY = CARE_OWN_COUNTRY
    OVERSEAS = CARE_OVERSEAS
    SINGAPORE = CARE_SINGAPORE
    OWN_COUNTRY_SINGAPORE = CARE_OWN_COUNTRY_SINGAPORE
    OWN_COUNTRY_OVERSEAS = CARE_OWN_COUNTRY_OVERSEAS
    OWN_COUNTRY_OVERSEAS_SINGPAPORE = CARE_OWN_COUNTRY_OVERSEAS_SINGPAPORE
    NO_EXP = CARE_NO_EXP
    NOT_WILLING = 'NW', _('Not willing to care for elderly')
    OTHERS = CARE_OTHERS


class DisabledCareRemarksChoices(models.TextChoices):
    OWN_COUNTRY = CARE_OWN_COUNTRY
    OVERSEAS = CARE_OVERSEAS
    SINGAPORE = CARE_SINGAPORE
    OWN_COUNTRY_SINGAPORE = CARE_OWN_COUNTRY_SINGAPORE
    OWN_COUNTRY_OVERSEAS = CARE_OWN_COUNTRY_OVERSEAS
    OWN_COUNTRY_OVERSEAS_SINGPAPORE = CARE_OWN_COUNTRY_OVERSEAS_SINGPAPORE
    NO_EXP = CARE_NO_EXP
    OTHERS = CARE_OTHERS


class GeneralHouseworkRemarksChoices(models.TextChoices):
    CAN_DO_ALL_HOUSEWORK = 'CAN', _('Able to do all general housework')
    OTHERS = CARE_OTHERS


class CookingRemarksChoices(models.TextChoices):
    OWN_COUNTRY = 'OC', _('Able to cook own country\'s cuisine')
    CHINESE = 'C', _('Able to cook chinese cuisine')
    INDIAN = 'I', _('Able to cook indian cuisine')
    WESTERN = 'W', _('Able to cook western cuisine')
    OWN_COUNTRY_CHINSE = 'OC_C', _(
        'Able to cook own country\'s and chinese cuisine'
    )
    OWN_COUNTRY_INDIAN = 'OC_I', _(
        'Able to cook own country\'s and indian cuisine'
    )
    OWN_COUNTRY_WESTERN = 'OC_W', _(
        'Able to cook own country\'s and western cuisine'
    )
    CHINESE_INDIAN = 'C_I', _(
        'Able to cook chinese and indian cuisine'
    )
    CHINESE_WESTERN = 'C_W', _(
        'Able to cook chinese and western cuisine'
    )
    INDIAN_WESTERN = 'I_W', _(
        'Able to cook indian and western cuisine'
    )
    OWN_COUNTRY_CHINESE_INDIAN = 'OC_C_I', _(
        'Able to cook own country\'s, chinese and indian cuisine'
    )
    OWN_COUNTRY_CHINESE_WESTERN = 'OC_C_W', _(
        'Able to cook own country\'s, chinese and western cuisine'
    )
    OWN_COUNTRY_INDIAN_WESTERN = 'OC_I_W', _(
        'Able to cook own country\'s, indian and western cuisine'
    )
    CHINESE_INDIAN_WESTERN = 'C_I_W', _(
        'Able to cook chinese, indian and western cuisine'
    )
    OWN_COUNTRY_CHINESE_INDIAN_WESTERN = 'OC_C_I_W', _(
        'Able to cook own country\'s, chinese, indian and western cuisine'
    )
    OTHERS = CARE_OTHERS


class MaidCareRemarksChoices(models.TextChoices):
    OWN_COUNTRY = CARE_OWN_COUNTRY
    OVERSEAS = CARE_OVERSEAS
    SINGAPORE = CARE_SINGAPORE
    OWN_COUNTRY_SINGAPORE = CARE_OWN_COUNTRY_SINGAPORE
    OWN_COUNTRY_OVERSEAS = CARE_OWN_COUNTRY_OVERSEAS
    OWN_COUNTRY_OVERSEAS_SINGPAPORE = CARE_OWN_COUNTRY_OVERSEAS_SINGPAPORE
    NO_EXP = CARE_NO_EXP
    OTHERS = CARE_OTHERS
