from rest_framework import serializers
from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    pct = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'limit_amount', 'currency',
            'month', 'year', 'spent', 'remaining', 'pct', 'status',
        ]

    def get_spent(self, obj):
        return float(obj.spent())

    def get_remaining(self, obj):
        return float(obj.remaining())
