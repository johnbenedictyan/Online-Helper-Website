# Imports from django
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

# Imports from foreign installed apps
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field

# Imports from local apps
from .forms import MaidLoanTransactionForm
from .models import Maid, MaidLoanTransaction

# Start of Formsets

MaidLoanTransactionFormSet = inlineformset_factory(
    parent_model=Maid,
    form=MaidLoanTransactionForm,
    model=MaidLoanTransaction,
    extra=1,
    min_num=1,
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
                            css_class='col-12 text-right'
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
