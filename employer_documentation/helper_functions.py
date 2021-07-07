from .constants import ResidentialStatusFullChoices


def is_local(rs):
    return (
        rs == ResidentialStatusFullChoices.SC or
        rs == ResidentialStatusFullChoices.PR
    )


def is_foreigner(rs):
    return not is_local(rs)
