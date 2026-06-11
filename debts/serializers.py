from rest_framework import serializers
from .models import Debt, DebtPayment


class DebtPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = ['id', 'debt', 'amount', 'date', 'note', 'created_at']
        read_only_fields = ['created_at']


class DebtSerializer(serializers.ModelSerializer):
    payments = DebtPaymentSerializer(many=True, read_only=True)
    paid_total = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    progress_pct = serializers.IntegerField(read_only=True)
    time_until_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Debt
        fields = [
            'id', 'person', 'amount', 'currency', 'debt_type',
            'date', 'deadline', 'interest_rate', 'note', 'is_settled',
            'payments', 'paid_total', 'remaining', 'progress_pct',
            'time_until_deadline', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_paid_total(self, obj):
        return float(obj.paid_total())

    def get_remaining(self, obj):
        return float(obj.remaining())

    def get_time_until_deadline(self, obj):
        return obj.time_until_deadline()
