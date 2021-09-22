from django import models


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
