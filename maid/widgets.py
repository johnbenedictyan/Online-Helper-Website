from django.forms import DateInput

class CustomDateInput(DateInput):
    template_name='widgets/custom-datepicker.html'