from .constants import (
    ResidentialStatusFullChoices, EmployerTypeOfApplicantChoices
)


def is_local(rs):
    return (
        rs == ResidentialStatusFullChoices.SC or
        rs == ResidentialStatusFullChoices.PR
    )


def is_foreigner(rs):
    return not is_local(rs)


def is_applicant_sponsor(type_of_applicant):
    return type_of_applicant == EmployerTypeOfApplicantChoices.SPONSOR


def is_applicant_joint_applicant(type_of_applicant):
    return type_of_applicant == EmployerTypeOfApplicantChoices.JOINT_APPLICANT


def is_applicant_spouse(type_of_applicant):
    return type_of_applicant == EmployerTypeOfApplicantChoices.SPOUSE
