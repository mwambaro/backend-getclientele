from rest_framework import serializers
from .models import Vendor, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Vendor
        fields = ('id', 'owner', 'business_name', 'is_mobile', 'lat', 'lng', 'address', 'categories', 'products')
        read_only_fields = ('owner',)
