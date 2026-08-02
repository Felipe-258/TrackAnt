from datetime import date
from django.db.models import Q


def cap_day(year, month, day):
    """Ajusta un día al máximo válido para el mes (ej: 31 en febrero → 28/29)."""
    import calendar
    last = calendar.monthrange(year, month)[1]
    return min(day, last)


def get_expense_category(colony_id, category=None):
    """Devuelve una categoría de gasto válida. Si no hay categoría o es inválida, busca una fallback."""
    from finances.models import Category
    if category:
        return category
    fallback = (
        Category.objects.filter(colony_id=colony_id, type='EXPENSE')
        .order_by('id')
        .first()
    )
    if fallback:
        return fallback
    return (
        Category.objects.filter(Q(colony_id=colony_id) | Q(colony__isnull=True), type='EXPENSE')
        .order_by('id')
        .first()
    )


def time_until_deadline(deadline, is_done=False):
    if not deadline or is_done:
        return None
    days = (deadline - date.today()).days
    if days < 0:
        return 'Vencida'
    if days == 0:
        return 'Hoy'
    if days == 1:
        return 'Mañana'
    if days <= 7:
        return f'{days} días'
    if days <= 30:
        weeks = days // 7
        return f'{weeks} {"semana" if weeks == 1 else "semanas"}'
    if days <= 365:
        months = days // 30
        return f'{months} {"mes" if months == 1 else "meses"}'
    years = days // 365
    return f'{years} {"año" if years == 1 else "años"}'
