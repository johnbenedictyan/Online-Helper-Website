# Django Imports
from django.forms.models import inlineformset_factory

# Foreign Apps Imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field

# App Imports
from .forms import MaidLoanTransactionForm, MaidEmploymentHistoryForm
from .models import Maid, MaidLoanTransaction, MaidEmploymentHistory

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
                            'date',
                            css_class='col-md-6'
                        ),
                        Column(
                            'description',
                            css_class='col-md-6'
                        ),
                        Column(
                            'amount',
                            css_class='col-md-6'
                        ),
                        Column(
                            'remarks',
                            css_class='col-md-6'
                        )
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
                            Row(
                                Column(
                                    Field(
                                        'start_date',
                                        type='text',
                                        onfocus="(this.type='date')",
                                        placeholder='Start date'
                                    ),
                                )
                            ),
                            Row(
                                Column(
                                    Field(
                                        'end_date',
                                        type='text',
                                        onfocus="(this.type='date')",
                                        placeholder='End date'
                                    ),
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'work_duties'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    ),
                    Row(
                        Column(
                            Row(
                                Column(
                                    'country'
                                )
                            ),
                            Row(
                                Column(
                                    'race_of_employer'
                                )
                            ),
                            css_class='col-md-6'
                        ),
                        Column(
                            Row(
                                Column(
                                    'reason_for_leaving'
                                )
                            ),
                            css_class='col-md-6'
                        )
                    )
                ),
                css_class='form-group'
            )
        )
        self.render_required_fields = True
