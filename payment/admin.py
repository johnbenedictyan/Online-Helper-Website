from django.contrib import admin
from .models import (
    Customer, SubscriptionProduct, SubscriptionProductImage,
    SubscriptionProductPrice, Subscription
)

# Register your models here.
admin.site.register(Customer)
admin.site.register(SubscriptionProduct)
admin.site.register(SubscriptionProductImage)
admin.site.register(SubscriptionProductPrice)
admin.site.register(Subscription)
