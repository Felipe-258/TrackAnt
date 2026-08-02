from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from decimal import Decimal, InvalidOperation
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


@api_view(['GET', 'POST'])
def api_rates(request):
    """GET: devuelve cotizaciones. POST: guarda manuales o fuerza fetch."""
    from ..exchange import fetch_exchange_rates, rates_stale, last_updated

    colony = request.colony
    currencies = Currency.objects.filter(Q(colony=colony) | Q(colony__isnull=True))

    if request.method == 'POST':
        action = request.data.get('action', '')
        if action == 'fetch':
            ok, msg = fetch_exchange_rates(force=True)
        elif action == 'save':
            saved = 0
            for c in currencies:
                val = request.data.get(f'rate_{c.code}')
                if val is not None:
                    try:
                        c.rate_to_base = Decimal(str(val)).quantize(Decimal('0.0001'))
                        c.save(update_fields=['rate_to_base'])
                        saved += 1
                    except (InvalidOperation, ValueError):
                        continue
            return Response({'ok': True, 'saved': saved, 'rates': {c.code: float(c.rate_to_base) for c in currencies}})
        else:
            return Response({'ok': False, 'detail': 'Acción inválida'}, status=400)
        return Response({'ok': ok, 'detail': msg, 'rates': {c.code: float(c.rate_to_base) for c in currencies}})

    return Response({
        'rates': {c.code: float(c.rate_to_base) for c in currencies},
        'updated_at': last_updated().isoformat() if last_updated() else None,
        'stale': rates_stale(),
    })
