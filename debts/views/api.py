from rest_framework import viewsets
from ..models import Debt, DebtPayment
from ..serializers import DebtSerializer, DebtPaymentSerializer


class DebtViewSet(viewsets.ModelViewSet):
    serializer_class = DebtSerializer
    filterset_fields = ['debt_type', 'is_settled']
    ordering = ['-date']

    def get_queryset(self):
        return Debt.objects.filter(colony=self.request.colony).select_related('currency').prefetch_related('payments')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)


class DebtPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = DebtPaymentSerializer
    filterset_fields = ['debt']
    ordering = ['-date']

    def get_queryset(self):
        return DebtPayment.objects.filter(debt__colony=self.request.colony).select_related('debt')

    def perform_create(self, serializer):
        serializer.save()
