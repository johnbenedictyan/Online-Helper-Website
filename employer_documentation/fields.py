# Django Imports
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from onlinemaid.fields import NullableCharField
from .constants import ResidentialStatusFullChoices


class CustomMoneyDecimalField(models.DecimalField):
    MONEY_VALIDATORS = [
        MinValueValidator(0),
        MaxValueValidator(10000)
    ]

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 7
        kwargs['decimal_places'] = 2
        kwargs['validators'] = self.MONEY_VALIDATORS
        super().__init__(*args, **kwargs)


class ResidentialStatusCharField(models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 5,
            'choices': ResidentialStatusFullChoices.choices,
            'default': ResidentialStatusFullChoices.SC
        })
        super().__init__(*args, **kwargs)


class NullableResidentialStatusCharField(NullableCharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 5,
            'choices': ResidentialStatusFullChoices.choices,
            'default': ResidentialStatusFullChoices.SC
        })
        super().__init__(*args, **kwargs)
