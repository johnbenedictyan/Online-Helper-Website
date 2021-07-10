# Django Imports
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# Foreign Apps Imports
import stripe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

# App Imports
from .models import (
    SubscriptionProduct, SubscriptionProductImage, SubscriptionProductPrice
)

stripe.api_key = settings.STRIPE_SECRET_KEY

# Start of Forms


class SubscriptionProductCreationForm(forms.ModelForm):
    class Meta:
        model = SubscriptionProduct
        exclude = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'name',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'description',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'active',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

    def clean_name(self):
        data = self.cleaned_data.get('name')
        stripe_products = stripe.Product.list()['data']
        for product in stripe_products:
            if product['name'] == data:
                msg = _('A product with this name already exist')
                self.add_error('name', msg)
        return data


class SubscriptionProductImageCreationForm(forms.ModelForm):
    class Meta:
        model = SubscriptionProductImage
        exclude = ['subscription_product']

    def __init__(self, *args, **kwargs):
        self.subscription_product_id = kwargs.pop(
            'subscription_product_id',
            None
        )
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'photo',
                    css_class='form-group col'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )

    def save(self, *args, **kwargs):
        self.instance.subscription_product = SubscriptionProduct.objects.get(
            pk=self.subscription_product_id
        )
        return super().save(*args, **kwargs)


class SubscriptionProductPriceCreationForm(forms.ModelForm):
    class Meta:
        model = SubscriptionProductPrice
        exclude = ['id', 'subscription_product']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    'unit_amount',
                    css_class='form-group col-md-6'
                ),
                Column(
                    'currency',
                    css_class='form-group col-md-6'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    'interval',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'interval_count',
                    css_class='form-group col-md-4'
                ),
                Column(
                    'active',
                    css_class='form-group col-md-4'
                ),
                css_class='form-row'
            ),
            Row(
                Column(
                    Submit(
                        'submit',
                        'Submit',
                        css_class="btn btn-primary w-50"
                    ),
                    css_class='form-group col-12 text-center'
                ),
                css_class='form-row'
            )
        )
