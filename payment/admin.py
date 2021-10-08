from django.contrib import admin

from .models import Customer, Subscription, SubscriptionPrice

# Register your models here.
admin.site.register(Customer)
admin.site.register(SubscriptionPrice)
admin.site.register(Subscription)
