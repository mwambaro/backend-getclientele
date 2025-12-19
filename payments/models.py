from django.db import models
from django.conf import settings


class BankerTransaction(models.Model):
    banker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='banker_transactions')
    shopper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shopper_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default='USD')
    type = models.CharField(max_length=32, default='deposit')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.amount} {self.currency}"


class VendorAccount(models.Model):
    vendor = models.OneToOneField('vendors.Vendor', on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Account {self.vendor} balance={self.balance}"


class Receipt(models.Model):
    session = models.ForeignKey('sessions_app.ShoppingSession', on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2)
    vendor_net = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.id} vendor={self.vendor} amount={self.amount}"


class Payout(models.Model):
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default='USD')
    stripe_transfer_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=32, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payout {self.id} vendor={self.vendor} amount={self.amount} status={self.status}"
