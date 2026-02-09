from rest_framework import serializers
from .models import Intent, ShoppingCart


class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = ('id', 'category', 'price_level', 'audience')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'item_name', 'item_price', 'total_sum_to_pay', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
