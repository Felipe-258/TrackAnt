import json
from decimal import Decimal, InvalidOperation
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from django.conf import settings
from django.db.models import Q, Sum
from django.utils import timezone

EXCHANGE_API_URL = getattr(settings, 'EXCHANGE_API_URL', 'https://open.er-api.com/v6/latest/USD')
EXCHANGE_INTERVAL_HOURS = getattr(settings, 'EXCHANGE_INTERVAL_HOURS', 6)


def available_balances(colony):
    """Devuelve {currency_code: balance_disponible} (ingresos - gastos - reservas) por moneda."""
    from .models import Transaction
    from goals.models import Reserve
    rows = (
        Transaction.objects.filter(colony=colony)
        .values('currency__code')
        .annotate(
            income=Sum('amount', filter=Q(type='INCOME')),
            expense=Sum('amount', filter=Q(type='EXPENSE')),
        )
    )
    balance = {
        r['currency__code']: float((r['income'] or 0) - (r['expense'] or 0))
        for r in rows
    }
    reserve_rows = (
        Reserve.objects.filter(colony=colony)
        .values('currency__code')
        .annotate(total=Sum('current_amount'))
    )
    for row in reserve_rows:
        balance[row['currency__code']] = balance.get(row['currency__code'], 0.0) - float(row['total'] or 0)
    return balance


def rates_stale():
    """True si las cotizaciones globales no se actualizaron dentro del intervalo."""
    from .models import Currency
    base = Currency.objects.filter(code='ARS', colony__isnull=True).first()
    if not base or not base.rates_updated_at:
        return True
    delta = timezone.now() - base.rates_updated_at
    return delta.total_seconds() > EXCHANGE_INTERVAL_HOURS * 3600


def last_updated():
    from .models import Currency
    base = Currency.objects.filter(code='ARS', colony__isnull=True).first()
    return base.rates_updated_at if base else None


def fetch_exchange_rates(force=False):
    """Trae cotizaciones de la API y actualiza Currency.rate_to_base (global).

    Devuelve (ok: bool, mensaje: str). Con TTL: si no está stale y no se fuerza, no llama a la API.
    """
    from .models import Currency

    if not force and not rates_stale():
        return False, 'Cotizaciones al día (no se llamó a la API)'

    try:
        with urlopen(EXCHANGE_API_URL, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except (URLError, HTTPError, ValueError, OSError) as e:
        return False, f'Error al contactar la API: {e}'

    usd_rates = data.get('rates', {})
    ars_per_usd = usd_rates.get('ARS')
    if not ars_per_usd:
        return False, 'La API no devolvió la cotización de ARS'

    now = timezone.now()
    updated = 0
    for cur in Currency.objects.filter(colony__isnull=True):
        usd_rate = usd_rates.get(cur.code)
        if not usd_rate:
            continue
        try:
            rate = Decimal(str(ars_per_usd)) / Decimal(str(usd_rate))
        except (InvalidOperation, ZeroDivisionError, ValueError):
            continue
        cur.rate_to_base = rate.quantize(Decimal('0.0001'))
        cur.rates_updated_at = now
        cur.save(update_fields=['rate_to_base', 'rates_updated_at'])
        updated += 1

    return True, f'Cotizaciones actualizadas ({updated} monedas)'


def convert(amount, from_code, to_code, rates):
    """Convierte amount (Decimal) de from_code a to_code usando dict rates {code: rate_to_base}.

    Devuelve Decimal o None si falta alguna moneda.
    """
    if not amount:
        return None
    if from_code == to_code:
        return amount
    from_rate = rates.get(from_code)
    to_rate = rates.get(to_code)
    if not from_rate or not to_rate:
        return None
    try:
        return Decimal(amount) * Decimal(str(from_rate)) / Decimal(str(to_rate))
    except (InvalidOperation, ZeroDivisionError, ValueError):
        return None
