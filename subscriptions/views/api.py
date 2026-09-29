from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Subscription, SubscriptionPayment
from ..serializers import SubscriptionSerializer, SubscriptionPaymentSerializer
from ..services import mark_as_paid, mark_as_unpaid


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    filterset_fields = ['is_active', 'cycle']
    ordering = ['next_date']

    def get_queryset(self):
        return Subscription.objects.filter(colony=self.request.colony).select_related('currency', 'category')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)


class SubscriptionPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionPaymentSerializer
    filterset_fields = ['is_paid', 'subscription']
    ordering = ['-due_date']

    def get_queryset(self):
        return SubscriptionPayment.objects.filter(
            subscription__colony=self.request.colony
        ).select_related('subscription__currency', 'subscription__category')

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        from decimal import Decimal, InvalidOperation
        payment = self.get_object()
        sub = payment.subscription
        if payment.is_paid:
            mark_as_unpaid(payment)
            return Response({'status': 'unpaid', 'message': f'{sub.name} marcada como no pagada'})
        else:
            amount = None
            if sub.is_variable:
                raw = request.data.get('amount')
                try:
                    amount = Decimal(str(raw))
                except (InvalidOperation, TypeError, ValueError):
                    return Response({'status': 'error', 'message': 'Ingresá el monto real de este período'}, status=status.HTTP_400_BAD_REQUEST)
                if amount <= 0:
                    return Response({'status': 'error', 'message': 'El monto debe ser mayor a cero'}, status=status.HTTP_400_BAD_REQUEST)
            transaction = mark_as_paid(payment, amount=amount)
            return Response({
                'status': 'paid',
                'message': f'{sub.name} marcada como pagada',
                'transaction_id': transaction.id,
            })
