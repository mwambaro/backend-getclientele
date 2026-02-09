from django.db import models


class Intent(models.Model):
    category = models.CharField(max_length=100, blank=True)
    price_level = models.CharField(max_length=50, blank=True)
    audience = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.category} - {self.price_level}'


class ShoppingCart(models.Model):
    item_name = models.CharField(max_length=255)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_sum_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name
