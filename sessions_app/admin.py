from django.contrib import admin
from .models import ShoppingSession


@admin.register(ShoppingSession)
class ShoppingSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'shopper', 'status', 'start_time')
