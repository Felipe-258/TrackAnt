from rest_framework import viewsets
from ..models import SplitGroup, SplitExpense
from ..serializers import SplitGroupSerializer, SplitExpenseSerializer


class SplitGroupViewSet(viewsets.ModelViewSet):
    serializer_class = SplitGroupSerializer
    ordering = ['-created_at']

    def get_queryset(self):
        return SplitGroup.objects.filter(colony=self.request.colony).prefetch_related('expenses__currency')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)


class SplitExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = SplitExpenseSerializer
    filterset_fields = ['group']
    ordering = ['-date']

    def get_queryset(self):
        return SplitExpense.objects.filter(colony=self.request.colony).select_related('currency')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)
