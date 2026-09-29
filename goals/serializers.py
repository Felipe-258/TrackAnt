from rest_framework import serializers
from .models import Reserve


class ReserveSerializer(serializers.ModelSerializer):
    progress_pct = serializers.IntegerField(read_only=True, allow_null=True)
    remaining = serializers.SerializerMethodField()
    time_until_deadline = serializers.SerializerMethodField()
    has_target = serializers.BooleanField(read_only=True)

    class Meta:
        model = Reserve
        fields = [
            'id', 'name', 'target_amount', 'current_amount',
            'currency', 'deadline', 'color', 'is_achieved',
            'has_target', 'progress_pct', 'remaining', 'time_until_deadline',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_remaining(self, obj):
        remaining = obj.remaining()
        return float(remaining) if remaining is not None else None

    def get_time_until_deadline(self, obj):
        return obj.time_until_deadline()
