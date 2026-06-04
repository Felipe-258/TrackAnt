from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from datetime import date
from ..models import Currency, Category, Tag, Transaction
from ..serializers import (
    CurrencySerializer, CategorySerializer,
    TagSerializer, TransactionSerializer,
)


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ['type']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('currency', 'category').prefetch_related('tags')
    serializer_class = TransactionSerializer
    filterset_fields = ['type', 'category', 'currency', 'is_recurring']
    search_fields = ['note', 'custom_tags']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs
