from rest_framework import viewsets
from ..models import Debt, DebtPayment
from ..serializers import DebtSerializer, DebtPaymentSerializer


class DebtViewSet(viewsets.ModelViewSet):
    queryset = Debt.objects.select_related('currency').prefetch_related('payments')
    serializer_class = DebtSerializer
    filterset_fields = ['debt_type', 'is_settled']
    ordering = ['-date']


class DebtPaymentViewSet(viewsets.ModelViewSet):
    queryset = DebtPayment.objects.select_related('debt')
    serializer_class = DebtPaymentSerializer
    filterset_fields = ['debt']
    ordering = ['-date']
