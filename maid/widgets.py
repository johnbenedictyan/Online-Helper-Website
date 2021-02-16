from django.forms import DateInput

class CustomDateInput(DateInput):
    template_name='widgets/custom-datepicker.html'

    def __init__(self, attrs=None):
        if attrs:
            if not attrs['placeholder']:
                attrs.update({
                    'placeholder': 'Select Date'
                })
        else:
            attrs = {
                'placeholder': 'Select Date'
            }
        super().__init__(attrs)