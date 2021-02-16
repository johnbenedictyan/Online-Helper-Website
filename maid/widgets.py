from django.forms import DateInput

class CustomDateInput(DateInput):
    template_name='widgets/custom-datepicker.html'

    def __init__(self, attrs=None):
        attrs = {
            'placeholder': 'Select Date'
        }
        super().__init__(attrs)