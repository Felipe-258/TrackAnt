from rest_framework import serializers
from .models import Goal


class GoalSerializer(serializers.ModelSerializer):
    progress_pct = serializers.IntegerField(read_only=True)
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            'id', 'name', 'target_amount', 'current_amount',
            'currency', 'deadline', 'color', 'is_achieved',
            'progress_pct', 'remaining', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_remaining(self, obj):
        return float(obj.remaining())
