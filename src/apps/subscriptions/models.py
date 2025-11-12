from decimal import Decimal, ROUND_HALF_UP

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

User = get_user_model()


class Tariff(models.Model):
    tariff_type = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(
        default=0, validators=[MaxValueValidator(100)]
    )

    def __str__(self):
        return f"id:{self.pk} | {self.discount_percent}%"


def get_default_tariff():
    return Tariff.objects.get(tariff_type="full").id


class SubscriptionPlan(models.Model):
    subscribe_type = models.CharField(max_length=128, unique=True)
    price = models.PositiveIntegerField()
    tariff = models.ForeignKey(
        Tariff,
        related_name="plans",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("subscribe_type",)

    def get_discount_percent(self):
        return self.tariff.discount_percent if self.tariff else 0

    def get_tariff_type(self):
        return self.tariff.tariff_type if self.tariff else None

    def get_price_with_discount(self):
        discount = Decimal(self.get_discount_percent())
        discounted = (Decimal(self.price) * (Decimal("100") - discount)) / Decimal(
            "100"
        )
        return discounted.quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        UserSubscription = apps.get_model("subscriptions", "UserSubscription")
        update_data = {
            "price": self.get_price_with_discount(),
        }
        if self.tariff_id:
            update_data["tariff_id"] = self.tariff_id
        UserSubscription.objects.filter(
            subscribe_type__iexact=self.subscribe_type
        ).update(**update_data)

    def __str__(self):
        return f"{self.subscribe_type} | {self.price}"


class UserSubscription(models.Model):
    subscribe_type = models.CharField(max_length=128)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tariff = models.ForeignKey(
        Tariff,
        related_name="subscriptions",
        on_delete=models.PROTECT,
        default=get_default_tariff,
    )
    price = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        try:
            plan = SubscriptionPlan.objects.get(
                subscribe_type__iexact=self.subscribe_type, is_active=True
            )
        except SubscriptionPlan.DoesNotExist as exc:
            raise ValidationError(
                f"План подписки '{self.subscribe_type}' не найден."
            ) from exc
        self.subscribe_type = plan.subscribe_type
        self.price = plan.get_price_with_discount()
        if plan.tariff:
            self.tariff = plan.tariff
        elif not self.tariff_id:
            self.tariff_id = get_default_tariff()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subscribe_type} | id:{self.pk} | {self.user}"
