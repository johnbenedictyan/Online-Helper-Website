from django.db import models
from django.utils.translation import ugettext_lazy as _

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

class ResidentialStatusChoices(models.TextChoices):
    SC = 'SC', _('Singapore citizen')
    PR = 'PR', _('Singapore permanent resident')

class MaritalStatusChoices(models.TextChoices):
    SINGLE = 'SINGLE', _('Single')
    MARRIED = 'MARRIED', _('Married')
    DIVORCED = 'DIVORCED', _('Divorced')
    WIDOWED = 'WIDOWED', _('Widowed')
    SEPARATED = 'SEPARATED', _('Separated')
