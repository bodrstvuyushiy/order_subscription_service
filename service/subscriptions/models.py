from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from service_app.config import SUBSCRIPTION_PRICES

User = get_user_model()


class Tariff(models.Model):
    TARIFF_TYPES = (
        ('full', 'Full'),
        ('discount', 'Discount'),
    )

    tariff_type = models.CharField(choices=TARIFF_TYPES, max_length=20, default='full')
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __str__(self):
        return f"id:{self.pk} | {self.discount_percent}%"


def get_default_tariff():
    return Tariff.objects.get(tariff_type='full').id


class UserSubscription(models.Model):
    SUBSCRIBE_TYPES = (
        ('human', 'Human'),
        ('mountain', 'Mountain'),
        ('sky', 'Sky'),
    )

    subscribe_type = models.CharField(choices=SUBSCRIBE_TYPES, max_length=128)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, related_name="subscriptions",
        on_delete=models.PROTECT, default=get_default_tariff)
    price = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.price = SUBSCRIPTION_PRICES.get(self.subscribe_type, 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subscribe_type} | id:{self.pk} | {self.user}"

