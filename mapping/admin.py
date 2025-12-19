from django.contrib import admin
from .models import AlleyTrace


@admin.register(AlleyTrace)
class AlleyTraceAdmin(admin.ModelAdmin):
    list_display = ('id', 'market_id', 'mapper', 'active', 'started_at')
