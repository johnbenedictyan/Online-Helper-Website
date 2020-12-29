# Imports from django
from django import forms

# Imports from foreign installed apps

# Imports from local apps

# Start of Fields
class MaidResponsibilityChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
         return f'{obj.get_name_display()}'