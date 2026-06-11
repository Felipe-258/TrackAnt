from rest_framework import viewsets, filters
from django.db.models import Q
from ..models import Currency, Category, Tag, Transaction
from ..serializers import (
    CurrencySerializer, CategorySerializer,
    TagSerializer, TransactionSerializer,
)


class CurrencyViewSet(viewsets.ModelViewSet):
    serializer_class = CurrencySerializer

    def get_queryset(self):
        colony = self.request.colony
        return Currency.objects.filter(Q(colony=colony) | Q(colony__isnull=True))

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    filterset_fields = ['type']

    def get_queryset(self):
        colony = self.request.colony
        return Category.objects.filter(Q(colony=colony) | Q(colony__isnull=True))

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        colony = self.request.colony
        return Tag.objects.filter(Q(colony=colony) | Q(colony__isnull=True))

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    filterset_fields = ['type', 'category', 'currency', 'is_recurring']
    search_fields = ['note', 'custom_tags']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        colony = self.request.colony
        qs = Transaction.objects.filter(colony=colony).select_related('currency', 'category').prefetch_related('tags')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)
