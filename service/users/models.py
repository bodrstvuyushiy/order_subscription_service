from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    telegram_id = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"user_id:{self.pk} {self.username}|"
