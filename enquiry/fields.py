# Django Imports
from django import forms

# Foreign Apps Imports

# App Imports

# Start of Fields
class MaidResponsibilityChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
         return f'{obj.get_name_display()}'