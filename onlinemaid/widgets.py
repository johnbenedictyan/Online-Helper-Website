from django import forms


class OMCustomTextarea(forms.Textarea):
    rows = 8
    cols = 16

    def __init__(self, attrs=None):
        attrs = {
            'cols': self.cols,
            'rows': self.rows
        }
        super().__init__(attrs=attrs)
