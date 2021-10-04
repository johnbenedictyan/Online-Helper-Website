

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Row
from django.forms.models import inlineformset_factory


from .forms import MaidEmploymentHistoryForm, MaidLoanTransactionForm
from .models import Maid, MaidEmploymentHistory, MaidLoanTransaction

# Start of Formsets

MaidLoanTransactionFormSet = inlineformset_factory(
    parent_model=Maid,
    form=MaidLoanTransactionForm,
    model=MaidLoanTransaction,
    extra=1,
    min_num=0,
    max_num=10
)


class MaidLoanTransactionFormSetHelper(FormHelper):
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
                            Field(
                                'date',
                                type='text',
                                onfocus="(this.type='date')"
                            ),
                            css_class='col-md-12 pr-md-3'
                        ),
                        Column(
                            'description',
                            css_class='col-md-12 pl-md-3'
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            'amount',
                            css_class='col-md-12 pr-md-3'
                        ),
                        css_class='form-row'
                    ),
                    Row(
                        Column(
                            'remarks',
                            css_class='col-md-24'
                        ),
                        css_class='form-row'
                    )
                ),
                css_class='form-group'
            )
        )
        self.render_required_fields = True


MaidEmploymentHistoryFormSet = inlineformset_factory(
    parent_model=Maid,
    form=MaidEmploymentHistoryForm,
    model=MaidEmploymentHistory,
    extra=1,
    min_num=0,
    max_num=10
)


class MaidEmploymentHistoryFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
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
                    Field(
                        'start_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='Start date'
                    ),
                    css_class='form-group col-md-12 pr-md-3'
                ),
                Column(
                    Field(
                        'end_date',
                        type='text',
                        onfocus="(this.type='date')",
                        placeholder='End date'
                    ),
                    css_class='form-group col-md-12 pl-md-3'
                ),
                Column(
                    'country',
                    css_class='form-group col-md-12 pr-md-3'
                ),
                Column(
                    'race_of_employer',
                    css_class='form-group col-md-12 pl-md-3'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'work_duties',
                    css_class='form-group col-md-12 pr-md-3'
                ),
                Column(
                    'reason_for_leaving',
                    css_class='form-group col-md-12 pl-md-3'
                ),
                css_class='form-row'
            )
        )
        self.render_required_fields = True
