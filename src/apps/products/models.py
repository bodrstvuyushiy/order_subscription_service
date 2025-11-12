from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class ProductItem(models.Model):
    name = models.CharField(max_length=128, unique=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.price})"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product_name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.pk} | {self.product_name}"

    def clean(self):
        if self.price is None or self.price <= 0:
            raise ValidationError({"price": "Цена должна быть больше нуля."})
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError({"quantity": "Количество должно быть больше нуля."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
