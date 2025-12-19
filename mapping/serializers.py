from rest_framework import serializers
from .models import AlleyTrace


class AlleyTraceStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlleyTrace
        fields = ('id', 'mapper', 'market_id', 'active', 'started_at')
        read_only_fields = ('id', 'active', 'started_at')


class AlleyTraceStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlleyTrace
        fields = ('id', 'points', 'stopped_at', 'active')
        read_only_fields = ('id', 'stopped_at')
