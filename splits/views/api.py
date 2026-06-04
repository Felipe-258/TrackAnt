from rest_framework import viewsets
from ..models import SplitGroup, SplitExpense
from ..serializers import SplitGroupSerializer, SplitExpenseSerializer


class SplitGroupViewSet(viewsets.ModelViewSet):
    queryset = SplitGroup.objects.prefetch_related('expenses__currency')
    serializer_class = SplitGroupSerializer
    ordering = ['-created_at']


class SplitExpenseViewSet(viewsets.ModelViewSet):
    queryset = SplitExpense.objects.select_related('currency')
    serializer_class = SplitExpenseSerializer
    filterset_fields = ['group']
    ordering = ['-date']
