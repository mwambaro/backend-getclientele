from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    nick_name = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=64, blank=True)
    region = models.CharField(max_length=64, blank=True)
    roles = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.username
