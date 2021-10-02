from .constants import MaidLanguageProficiencyChoices, TypeOfMaidChoices


def is_maid_new(maid_type):
    return maid_type == TypeOfMaidChoices.NEW


def is_able_to_speak(LanguageProficiency):
    return LanguageProficiency != MaidLanguageProficiencyChoices.UNABLE


def is_not_able_to_speak(LanguageProficiency):
    return not is_able_to_speak(LanguageProficiency)
