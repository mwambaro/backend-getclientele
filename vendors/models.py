from django.db import models
from django.conf import settings


class Vendor(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendors')
    business_name = models.CharField(max_length=255)
    is_mobile = models.BooleanField(default=False)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=512, blank=True)
    categories = models.JSONField(default=list, blank=True)
    visit_count = models.IntegerField(default=0)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.business_name


class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='USD')
    stock = models.IntegerField(default=0)
