from rest_framework import serializers
from .models import Receipt, Payout


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ('commission', 'vendor_net', 'timestamp')


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = '__all__'
        read_only_fields = ('stripe_transfer_id', 'status', 'created_at')
