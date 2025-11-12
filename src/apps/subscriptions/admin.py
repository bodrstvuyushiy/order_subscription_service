from django.contrib import admin

from .models import SubscriptionPlan, Tariff, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("subscribe_type", "price", "tariff", "is_active")
    list_filter = ("is_active", "tariff")
    search_fields = ("subscribe_type",)


admin.site.register(Tariff)
admin.site.register(UserSubscription)
