from django import forms


class OMCustomTextarea(forms.Textarea):
    rows = 8
    cols = 16

    def __init__(self, attrs=None):
        custom_attrs = {
            'cols': self.cols,
            'rows': self.rows
        }
        if attrs:
            custom_attrs.update(
                attrs
            )
        super().__init__(attrs=custom_attrs)
