from rest_framework import viewsets
from ..models import Budget
from ..serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('category', 'currency')
    serializer_class = BudgetSerializer
    filterset_fields = ['month', 'year', 'category']
    ordering = ['category__name']
