from django.db import models
from django.conf import settings


class ShoppingSession(models.Model):
    shopper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    intent = models.TextField(blank=True)
    cart = models.JSONField(default=list, blank=True)
    route_stops = models.JSONField(default=list, blank=True)
    receipts = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, default='active')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} ({self.shopper})"
