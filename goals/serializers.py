from rest_framework import serializers
from .models import Goal


class GoalSerializer(serializers.ModelSerializer):
    progress_pct = serializers.IntegerField(read_only=True)
    remaining = serializers.SerializerMethodField()
    time_until_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            'id', 'name', 'target_amount', 'current_amount',
            'currency', 'deadline', 'color', 'is_achieved',
            'progress_pct', 'remaining', 'time_until_deadline',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_remaining(self, obj):
        return float(obj.remaining())

    def get_time_until_deadline(self, obj):
        return obj.time_until_deadline()
