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

class DayChoices(models.IntegerChoices):
    D00 = 0, _("0 days")
    D01 = 1, _("1 day")
    D02 = 2, _("2 days")
    D03 = 3, _("3 days")
    D04 = 4, _("4 days")
    D05 = 5, _("5 days")
    D06 = 6, _("6 days")
    D07 = 7, _("7 days")
    D08 = 8, _("8 days")
    D09 = 9, _("9 days")
    D10 = 10, _("10 days")
    D11 = 11, _("11 days")
    D12 = 12, _("12 days")
    D13 = 13, _("13 days")
    D14 = 14, _("14 days")
    D15 = 15, _("15 days")
    D16 = 16, _("16 days")
    D17 = 17, _("17 days")
    D18 = 18, _("18 days")
    D19 = 19, _("19 days")
    D20 = 20, _("20 days")
    D21 = 21, _("21 days")
    D22 = 22, _("22 days")
    D23 = 23, _("23 days")
    D24 = 24, _("24 days")
    D25 = 25, _("25 days")
    D26 = 26, _("26 days")
    D27 = 27, _("27 days")
    D28 = 28, _("28 days")

class WeekChoices(models.IntegerChoices):
    W00 = 0, _("0 weeks")
    W01 = 1, _("1 week")
    W02 = 2, _("2 weeks")
    W03 = 3, _("3 weeks")
    W04 = 4, _("4 weeks")

class MonthChoices(models.IntegerChoices):
    M00 = 0, _("0 months")
    M01 = 1, _("1 month")
    M02 = 2, _("2 months")
    M03 = 3, _("3 months")
    M04 = 4, _("4 months")
    M05 = 5, _("5 months")
    M06 = 6, _("6 months")
    M07 = 7, _("7 months")
    M08 = 8, _("8 months")
    M09 = 9, _("9 months")
    M10 = 10, _("10 months")
    M11 = 11, _("11 months")
    M12 = 12, _("12 months")
    M13 = 13, _("13 months")
    M14 = 14, _("14 months")
    M15 = 15, _("15 months")
    M16 = 16, _("16 months")
    M17 = 17, _("17 months")
    M18 = 18, _("18 months")
    M19 = 19, _("19 months")
    M20 = 20, _("20 months")
    M21 = 21, _("21 months")
    M22 = 22, _("22 months")
    M23 = 23, _("23 months")
    M24 = 24, _("24 months")

class EmployerTypeOfApplicantChoices(models.TextChoices):
    SINGLE = 'SINGLE', _("Employer Only")
    SPOUSE = 'SPOUSE', _("Employer with Spouse")
    SPONSOR = 'SPONSR', _("Employer with Sponsor(s)")
    JOINT_APPLICANT = 'JNT_AP', _("Employer with Joint Applicant")

monthly_income_label = {
    EmployerTypeOfApplicantChoices.SINGLE: ['Employer Monthly Income', 'Have you worked in Singapore for the last 2 Years?'],
    EmployerTypeOfApplicantChoices.SPOUSE: ['Employer and Spouse Combined Monthly Income', 'Have you worked in Singapore for the last 2 Years?'],
    EmployerTypeOfApplicantChoices.SPONSOR: ['Sponsor(s) Monthly Income', 'Have you worked in Singapore for the last 2 Years?'],
    EmployerTypeOfApplicantChoices.JOINT_APPLICANT: ['Employer and Joint Applicant Combined Monthly Income', 'Have you worked in Singapore for the last 2 Years?'],
}

class DayOfWeekChoices(models.TextChoices):
    MONDAY = 'MONDAY', _('Monday')
    TUESDAY = 'TUESDAY', _('Tuesday')
    WEDNESDAY = 'WEDNESDAY', _('Wednesday')
    THURSDAY = 'THURSDAY', _('Thursday')
    FRIDAY = 'FRIDAY', _('Friday')
    SATURDAY = 'SATURDAY', _('Saturday')
    SUNDAY = 'SUNDAY', _('Sunday')