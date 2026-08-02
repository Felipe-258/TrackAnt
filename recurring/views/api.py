from rest_framework import viewsets
from ..models import RecurringTransaction
from ..serializers import RecurringTransactionSerializer


class RecurringTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringTransactionSerializer
    filterset_fields = ['is_active', 'cycle', 'currency__code']

    def get_queryset(self):
        return RecurringTransaction.objects.filter(colony=self.request.colony).select_related('currency', 'category')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)
