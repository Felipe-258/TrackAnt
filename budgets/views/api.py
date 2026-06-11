from rest_framework import viewsets
from ..models import Budget
from ..serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    filterset_fields = ['month', 'year', 'category']
    ordering = ['category__name']

    def get_queryset(self):
        return Budget.objects.filter(colony=self.request.colony).select_related('category', 'currency')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)
