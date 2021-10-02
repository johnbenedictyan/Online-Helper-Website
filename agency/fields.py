from django.db import models

from .constants import OpeningHoursChoices


class OpeningHoursField(models.CharField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.update({
            'max_length': 8,
            'choices': OpeningHoursChoices.choices,
            'default': OpeningHoursChoices.TIME0000
        })
        super().__init__(*args, **kwargs)
