from rest_framework import serializers
from .models import SplitGroup, SplitExpense


class SplitExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SplitExpense
        fields = ['id', 'group', 'description', 'amount', 'currency', 'paid_by', 'date', 'shares', 'created_at']
        read_only_fields = ['created_at']


class SplitGroupSerializer(serializers.ModelSerializer):
    expenses = SplitExpenseSerializer(many=True, read_only=True)
    total_spent = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = SplitGroup
        fields = ['id', 'name', 'members', 'expenses', 'total_spent', 'balance', 'created_at']
        read_only_fields = ['created_at']

    def get_total_spent(self, obj):
        return float(obj.total_spent())

    def get_balance(self, obj):
        return obj.balance()
