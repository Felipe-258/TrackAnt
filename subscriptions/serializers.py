from rest_framework import serializers
from .models import Subscription, SubscriptionPayment


class SubscriptionSerializer(serializers.ModelSerializer):
    monthly_cost = serializers.FloatField(read_only=True)
    days_until_next = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'name', 'amount', 'currency', 'cycle',
            'next_date', 'category', 'is_active', 'is_variable', 'auto_debit',
            'monthly_cost', 'days_until_next', 'created_at',
        ]
        read_only_fields = ['created_at']


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    subscription_name = serializers.CharField(source='subscription.name', read_only=True)
    subscription_amount = serializers.DecimalField(source='subscription.amount', max_digits=10, decimal_places=2, read_only=True)
    subscription_currency_symbol = serializers.CharField(source='subscription.currency.symbol', read_only=True)

    class Meta:
        model = SubscriptionPayment
        fields = [
            'id', 'subscription', 'subscription_name', 'subscription_amount',
            'subscription_currency_symbol', 'due_date', 'is_paid',
            'paid_date', 'transaction', 'created_at',
        ]
        read_only_fields = ['created_at', 'paid_date', 'transaction']
