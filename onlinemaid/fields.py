from django.db import models

from .constants import GenderChoices, FullNationsChoices, MaritalStatusChoices


class CustomBinaryField(models.BinaryField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'editable': True,
            'blank': True,
            'null': True
        })
        super().__init__(*args, **kwargs)


class NullableCharField(models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'blank': True,
            'null': True
        })
        super().__init__(*args, **kwargs)


class NullableBooleanField(models.BooleanField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'blank': True,
            'null': True
        })
        super().__init__(*args, **kwargs)


class GenderCharField(models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 1,
            'choices': GenderChoices.choices,
            'default': GenderChoices.F
        })
        super().__init__(*args, **kwargs)


class NullableGenderCharField(NullableCharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 1,
            'choices': GenderChoices.choices,
            'default': GenderChoices.F
        })
        super().__init__(*args, **kwargs)


class NationalityCharField(models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 3,
            'choices': FullNationsChoices.choices,
            'default': FullNationsChoices.SINGAPORE
        })
        super().__init__(*args, **kwargs)


class NullableNationalityCharField(NullableCharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 3,
            'choices': FullNationsChoices.choices,
            'default': FullNationsChoices.SINGAPORE
        })
        super().__init__(*args, **kwargs)


class NullableDateField(models.DateField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'blank': True,
            'null': True
        })
        super().__init__(*args, **kwargs)


class MaritalStatusCharField(models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 10,
            'choices': MaritalStatusChoices.choices,
            'default': MaritalStatusChoices.SINGLE
        })
        super().__init__(*args, **kwargs)


class NullableMaritalStatusCharField(NullableCharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 10,
            'choices': MaritalStatusChoices.choices,
            'default': MaritalStatusChoices.SINGLE
        })
        super().__init__(*args, **kwargs)
