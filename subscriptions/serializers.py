from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    monthly_cost = serializers.FloatField(read_only=True)
    days_until_next = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'name', 'amount', 'currency', 'cycle',
            'next_date', 'category', 'is_active',
            'monthly_cost', 'days_until_next', 'created_at',
        ]
        read_only_fields = ['created_at']
