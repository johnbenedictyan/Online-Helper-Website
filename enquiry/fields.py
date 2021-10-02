# Django Imports
from django import forms


# Start of Fields
class MaidResponsibilityChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.get_name_display()}'
