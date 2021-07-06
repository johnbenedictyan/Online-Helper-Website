from django.forms import DateInput
from django_filters.widgets import RangeWidget


class CustomDateInput(DateInput):
    template_name = 'widgets/custom-date.html'

    def __init__(self, attrs=None):
        if attrs:
            if 'placeholder' not in attrs:
                attrs.update({
                    'placeholder': 'Select Date'
                })
        else:
            attrs = {
                'placeholder': 'Select Date'
            }
        super().__init__(attrs)


class CustomRangeWidget(RangeWidget):
    template_name = 'widgets/custom-range.html'
