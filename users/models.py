from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


TAB_BAR_DEFAULTS = [
    {'slug': 'dashboard', 'url': 'finances:dashboard', 'icon': 'layout-dashboard', 'label': 'Home',
     'active_view': 'finances:dashboard', 'active_ns': None, 'active_contains': None, 'visible': True},
    {'slug': 'analytics', 'url': 'finances:analytics', 'icon': 'chart-bar', 'label': 'Análisis',
     'active_view': 'finances:analytics', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'income', 'url': 'finances:income_list', 'icon': 'trending-up', 'label': 'Ingresos',
     'active_view': None, 'active_ns': None, 'active_contains': 'income', 'visible': True},
    {'slug': 'expense', 'url': 'finances:expense_list', 'icon': 'trending-down', 'label': 'Gastos',
     'active_view': None, 'active_ns': None, 'active_contains': 'expense', 'visible': True},
    {'slug': 'transactions', 'url': 'finances:transaction_list', 'icon': 'list', 'label': 'Transacciones',
     'active_view': 'finances:transaction_list', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'reserves', 'url': 'reserves:list', 'icon': 'piggy-bank', 'label': 'Reservas',
     'active_view': None, 'active_ns': 'reserves', 'active_contains': None, 'visible': True},
    {'slug': 'budgets', 'url': 'budgets:budget_list', 'icon': 'piggy-bank', 'label': 'Presupuestos',
     'active_view': 'budgets:budget_list', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'debts', 'url': 'debts:debt_list', 'icon': 'scale', 'label': 'Deudas',
     'active_view': 'debts:debt_list', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'subscriptions', 'url': 'subscriptions:subscription_list', 'icon': 'repeat', 'label': 'Suscripciones',
     'active_view': 'subscriptions:subscription_list', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'splits', 'url': 'splits:split_list', 'icon': 'users', 'label': 'Splits',
     'active_view': 'splits:split_list', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'installments', 'url': 'installments:list', 'icon': 'shopping-cart', 'label': 'Cuotas',
     'active_view': None, 'active_ns': 'installments', 'active_contains': None, 'visible': False},
    {'slug': 'categories', 'url': 'finances:category_list', 'icon': 'folder-tree', 'label': 'Categorías',
     'active_view': 'finances:category_list', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'conversion', 'url': 'finances:conversion', 'icon': 'dollar-sign', 'label': 'Conversión',
     'active_view': 'finances:conversion', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'settings', 'url': 'users:settings', 'icon': 'settings', 'label': 'Ajustes',
     'active_view': 'users:settings', 'active_ns': None, 'active_contains': None, 'visible': False},
    {'slug': 'colony', 'url': 'ants:colony_view', 'icon': 'bug', 'label': 'Colonia',
     'active_view': None, 'active_ns': 'ants', 'active_contains': None, 'visible': False},
]

TAB_ICON_CHOICES = ['layout-dashboard', 'trending-up', 'trending-down', 'target', 'piggy-bank', 'scale',
                    'repeat', 'users', 'shopping-cart', 'folder-tree', 'dollar-sign', 'settings', 'bug',
                    'wallet', 'credit-card', 'coins', 'home', 'star', 'heart', 'gift', 'bell', 'book-open',
                    'calendar', 'chart-bar', 'shield', 'sparkles', 'zap', 'list', 'receipt-text']


def effective_tab_config(colony):
    """Resuelve config de barra inferior: defaults + overrides por colonia, respetando orden."""
    stored = colony.tab_bar_config if colony and colony.tab_bar_config else []
    known = {t['slug']: t for t in TAB_BAR_DEFAULTS}
    merged = []
    seen = set()
    for s in stored:
        slug = s.get('slug')
        if slug in known and slug not in seen:
            t = known[slug]
            entry = dict(t)
            entry['icon'] = s.get('icon') or t['icon']
            entry['label'] = (s.get('label') or '').strip() or t['label']
            entry['visible'] = bool(s.get('visible', t['visible']))
            merged.append(entry)
            seen.add(slug)
    for t in TAB_BAR_DEFAULTS:
        if t['slug'] not in seen:
            merged.append(dict(t))
    return merged


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Colony(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_colonies',
        null=True,
        blank=True,
        verbose_name='Dueño',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='colonies',
        blank=True,
        verbose_name='Miembros',
    )
    is_guest = models.BooleanField(default=False, verbose_name='Es invitado')
    default_currency = models.ForeignKey(
        'finances.Currency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='colony_defaults',
        verbose_name='Moneda por defecto',
    )
    auto_create_debt_transactions = models.BooleanField(
        default=False,
        verbose_name='Crear gasto al pagar deuda',
    )
    auto_create_split_transactions = models.BooleanField(
        default=False,
        verbose_name='Crear gasto en splits',
    )
    require_funds_for_conversion = models.BooleanField(
        default=True,
        verbose_name='Exigir fondos para convertir',
        help_text='Impide convertir más de lo que tenés disponible en esa moneda',
    )
    budget_alert_threshold = models.IntegerField(
        default=80,
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        verbose_name='Umbral de alerta de presupuesto (%)',
    )
    debt_show_days = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name='Mostrar deudas con deadline en (días)',
    )
    tab_bar_config = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Barra inferior (PWA)',
    )
    ant_expense_max_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('5000.00'),
        verbose_name='Gasto hormiga: monto máximo',
        help_text='Tope absoluto por transacción para considerarla gasto hormiga',
    )
    ant_expense_income_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.10')), MaxValueValidator(Decimal('100'))],
        verbose_name='Gasto hormiga: % del ingreso',
        help_text='Tope relativo al ingreso mensual. El umbral efectivo es el menor de ambos',
    )
    ant_expense_min_count = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        verbose_name='Gasto hormiga: mínimo de transacciones',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Colonia'
        verbose_name_plural = 'Colonias'
        ordering = ['name']

    def __str__(self):
        return self.name
