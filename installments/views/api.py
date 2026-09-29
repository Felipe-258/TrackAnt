from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import InstallmentPurchase, Installment
from ..serializers import InstallmentPurchaseSerializer, InstallmentSerializer


class InstallmentPurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = InstallmentPurchaseSerializer
    filterset_fields = ['is_completed', 'currency__code']

    def get_queryset(self):
        return InstallmentPurchase.objects.filter(colony=self.request.colony).select_related('currency', 'category').prefetch_related('installments')

    def perform_create(self, serializer):
        purchase = serializer.save(colony=self.request.colony)
        from .pages import _create_installments
        _create_installments(purchase)


class InstallmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InstallmentSerializer
    filterset_fields = ['is_paid', 'purchase']

    def get_queryset(self):
        return Installment.objects.filter(purchase__colony=self.request.colony).select_related('purchase', 'purchase__currency', 'transaction')

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        installment = self.get_object()
        if installment.is_paid:
            return Response({'detail': 'Ya pagada'}, status=status.HTTP_400_BAD_REQUEST)

        if request.colony.require_funds_for_conversion:
            from finances.exchange import available_balances
            avail = available_balances(request.colony).get(installment.purchase.currency.code, 0)
            if installment.amount > avail:
                return Response({'detail': f'No tenés suficientes {installment.purchase.currency.code} (disponible: {avail:,.2f})'}, status=status.HTTP_400_BAD_REQUEST)

        from trackant.utils import get_expense_category
        from finances.models import Transaction
        from django.utils import timezone
        tx = Transaction.objects.create(
            colony=request.colony,
            type='EXPENSE',
            amount=installment.amount,
            currency=installment.purchase.currency,
            category=get_expense_category(request.colony.id, installment.purchase.category),
            date=timezone.now().date(),
            note=f'Cuota {installment.number}/{installment.purchase.installments_count} - {installment.purchase.name}',
        )
        installment.is_paid = True
        installment.paid_date = timezone.now().date()
        installment.transaction = tx
        installment.save()

        from .pages import _check_completed
        _check_completed(installment.purchase)

        return Response(InstallmentSerializer(installment).data)
