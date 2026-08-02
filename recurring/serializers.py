from rest_framework import serializers
from .models import RecurringTransaction


class RecurringTransactionSerializer(serializers.ModelSerializer):
    monthly_cost = serializers.FloatField(read_only=True)
    days_until_next = serializers.IntegerField(read_only=True)

    class Meta:
        model = RecurringTransaction
        fields = '__all__'
