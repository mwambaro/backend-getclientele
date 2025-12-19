from rest_framework import serializers
from .models import ShoppingSession


class ShoppingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingSession
        fields = '__all__'
        read_only_fields = ('shopper', 'start_time', 'end_time')
