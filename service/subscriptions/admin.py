from django.contrib import admin

from subscriptions.models import Tariff, UserSubscription

admin.site.register(Tariff)
admin.site.register(UserSubscription)