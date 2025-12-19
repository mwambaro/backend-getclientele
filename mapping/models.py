from django.db import models
from django.conf import settings


class AlleyTrace(models.Model):
    mapper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    market_id = models.CharField(max_length=128)
    points = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Trace {self.id} for {self.market_id}"
