from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Row
from django.forms.models import inlineformset_factory

from .forms import EmployerHouseholdDetailsForm, MaidInventoryForm
from .models import Employer, EmployerDoc, EmployerHousehold, MaidInventory

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
                            css_class='col-24 text-right'
                        )
                    ),
                    Row(
                        Column(
                            'household_name',
                            css_class='col-lg-12 pr-md-3'
                        ),
                        Column(
                            'household_id_type',
                            css_class='col-lg-12 pl-md-3',
                        ),
                        Column(
                            'household_id_num',
                            css_class='col-xl-12 pr-md-3'
                        ),
                        Column(
                            Field(
                                'household_date_of_birth',
                                type='text',
                                onfocus="(this.type='date')",
                                placeholder='Date of birth'
                            ),
                            css_class='col-xl-12 pl-md-3',
                        ),
                        Column(
                            'household_relationship',
                            css_class='col-xl-12 pr-md-3'
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
                            css_class='col-24 text-right'
                        )
                    ),
                    Row(
                        Column(
                            'item_name',
                            css_class='col-md-12'
                        )
                    )
                ),
                css_class='form-group'
            )
        )
        self.render_required_fields = True
