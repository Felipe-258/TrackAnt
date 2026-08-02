from rest_framework import serializers
from .models import InstallmentPurchase, Installment


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = '__all__'


class InstallmentPurchaseSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)
    paid_count = serializers.IntegerField(read_only=True)
    remaining_count = serializers.IntegerField(read_only=True)
    paid_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    progress_pct = serializers.IntegerField(read_only=True)

    class Meta:
        model = InstallmentPurchase
        fields = '__all__'
