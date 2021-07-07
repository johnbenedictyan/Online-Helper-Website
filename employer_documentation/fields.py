from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


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
