# Imports from django
from django.forms.models import inlineformset_factory

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field

# Imports from local apps
from .forms import EmployerHouseholdDetailsForm, MaidInventoryForm
from .models import Employer, EmployerHousehold, EmployerDoc, MaidInventory

# Start of Formsets

EmployerHouseholdFormSet = inlineformset_factory(
    parent_model=Employer,
    form=EmployerHouseholdDetailsForm,
    model=EmployerHousehold,
    extra=1,
    min_num=0,
    max_num=10
)


class EmployerHouseholdFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            Field(
                                'DELETE'
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            'household_name',
                            css_class='col-md-6'
                        ),
                        Column(
                            'household_id_type',
                            css_class='col-md-6',
                        ),
                        Column(
                            'household_id_num',
                            css_class='col-md-6'
                        ),
                        Column(
                            'household_date_of_birth',
                            css_class='col-md-6',
                        ),
                        Column(
                            'household_relationship',
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class='form-group',
            )
        )
        self.render_required_fields = True


MaidInventoryFormSet = inlineformset_factory(
    parent_model=EmployerDoc,
    form=MaidInventoryForm,
    model=MaidInventory,
    extra=1,
    min_num=0,
    max_num=20
)


class MaidInventoryFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            Row(
                Column(
                    Row(
                        Column(
                            Field(
                                'DELETE'
                            ),
                            css_class='col-12 text-right'
                        )
                    ),
                    Row(
                        Column(
                            'item_name',
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class='form-group'
            )
        )
        self.render_required_fields = True
