from django.db import models
from django.utils.translation import ugettext_lazy as _

class IncomeChoices(models.IntegerChoices):
    INCOME_0 = 0, _("Below $2,000")
    INCOME_1 = 1, _("$2,000 to $2,499")
    INCOME_2 = 2, _("$2,500 to $2,999")
    INCOME_3 = 3, _("$3,000 to $3,499")
    INCOME_4 = 4, _("$3,500 to $3,999")
    INCOME_5 = 5, _("$4,000 to $4,999")
    INCOME_6 = 6, _("$5,000 to $5,999")
    INCOME_7 = 7, _("$6,000 to $7,999")
    INCOME_8 = 8, _("$8,000 to $9,999")
    INCOME_9 = 9, _("$10,000 to $12,499")
    INCOME_10 = 10, _("$12,500 to $14,999")
    INCOME_11 = 11, _("$15,000 to $19,999")
    INCOME_12 = 12, _("$20,000 to $24,999")
    INCOME_13 = 13, _("$25,000 and above")

class RelationshipChoices(models.TextChoices):
    SON = 'SON', _('Son')
    DAUGHTER = 'DAUGHTER', _('Daughter')
    FATHER = 'FATHER', _('Father')
    MOTHER = 'MOTHER', _('Mother')
    GRANDFATHER = 'GRANDFATHER', _('Grandfather')
    GRANDMOTHER = 'GRANDMOTHER', _('Grandmother')
    BROTHER = 'BROTHER', _('Brother')
    SISTER = 'SISTER', _('Sister')
    FATHER_IN_LAW = 'FATHER_IN_LAW', _('Father-in-law')
    MOTHER_IN_LAW = 'MOTHER_IN_LAW', _('Mother-in-law')
    SON_IN_LAW = 'SON_IN_LAW', _('Son-in-law')
    DAUGHTER_IN_LAW = 'DAUGHTER_IN_LAW', _('Daughter-in-law')
    GRANDDAUGHTER = 'GRANDDAUGHTER', _('Granddaughter')
    GRANDSON = 'GRANDSON', _('Grandson')
    BROTHER_IN_LAW = 'BROTHER_IN_LAW', _('Brother-in-law')
    SISTER_IN_LAW = 'SISTER_IN_LAW', _('Sister-in-law')
    GRANDFATHER_IN_LAW = 'GRANDFATHER_IN_LAW', _('Grandfather-in-law')
    GRANDMOTHER_IN_LAW = 'GRANDMOTHER_IN_LAW', _('Grandmother-in-law')
    YOUNG_CHILD_LEGAL_WARD = 'YOUNG_CHILD_LEGAL_WARD', _('Young child legal ward')
    AGED_PERSON_LEGAL = 'AGED_PERSON_LEGAL_WARD', _('Aged person legal ward')
    OTHER = 'OTHER', _('Other')

class GenderChoices(models.TextChoices):
    M = 'M', _('Male')
    F = 'F', _('Female')

class ResidentialStatusFullChoices(models.TextChoices):
    SC = 'SC', _('Singapore citizen')
    PR = 'PR', _('Singapore permanent resident')
    LTVP = 'LTVP', _('Long-Term Visit Pass')
    EP_SP = 'EP', _('Employment Pass or S Pass')
    DEPEN = 'DEPEN', _("Dependant's Pass")
    DIPLO = 'DIPLO', _('Diplomat')
    OTHER = 'OTHER', _('Others')

class ResidentialStatusPartialChoices(models.TextChoices):
    SC = 'SC', _('Singapore citizen')
    PR = 'PR', _('Singapore permanent resident')

class MaritalStatusChoices(models.TextChoices):
    SINGLE = 'SINGLE', _('Single')
    MARRIED = 'MARRIED', _('Married')
    DIVORCED = 'DIVORCED', _('Divorced')
    WIDOWED = 'WIDOWED', _('Widowed')
    SEPARATED = 'SEPARATED', _('Separated')

class HouseholdIdTypeChoices(models.TextChoices):
    NRIC = 'NRIC', _('NRIC')
    BC = 'BC', _('Birth Certificate')
