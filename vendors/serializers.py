from rest_framework import serializers
from .models import Vendor, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'vendor', 'product_name', 'product_sell_price', 'product_purchase_price', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class VendorSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Vendor
        fields = ('id', 'owner', 'business_name', 'is_mobile', 'lat', 'lng', 'address', 'categories', 'products', 'visit_count', 'stripe_account_id')
        read_only_fields = ('owner', 'id')
