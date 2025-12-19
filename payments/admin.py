from django.contrib import admin
from .models import BankerTransaction


@admin.register(BankerTransaction)
class BankerTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'banker', 'shopper', 'amount', 'currency', 'type', 'timestamp')
