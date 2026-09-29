from django.db import models
from django.db.models import Q


class Currency(models.Model):
    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Colonia')
    code = models.CharField(max_length=3, unique=True, verbose_name='Código')
    symbol = models.CharField(max_length=5, verbose_name='Símbolo')
    name = models.CharField(max_length=50, verbose_name='Nombre')
    rate_to_base = models.DecimalField(max_digits=10, decimal_places=4, default=1.0,
                                       help_text='Tasa respecto a la moneda base (ARS=1.0)')
    rates_updated_at = models.DateTimeField(null=True, blank=True, verbose_name='Cotizaciones actualizadas')

    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
        ordering = ['code']

    def __str__(self):
        return f'{self.symbol} {self.code}'


class Category(models.Model):
    class Type(models.TextChoices):
        INCOME = 'INCOME', 'Ingreso'
        EXPENSE = 'EXPENSE', 'Gasto'

    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Colonia')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    type = models.CharField(max_length=7, choices=Type.choices, verbose_name='Tipo')
    icon = models.CharField(max_length=50, blank=True, default='package', verbose_name='Ícono')
    color = models.CharField(max_length=7, blank=True, default='#A07858', verbose_name='Color')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['type', 'name']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class Type(models.TextChoices):
        INCOME = 'INCOME', 'Ingreso'
        EXPENSE = 'EXPENSE', 'Gasto'

    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia', db_index=True)
    type = models.CharField(max_length=7, choices=Type.choices, verbose_name='Tipo', db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name='Moneda')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoría')
    date = models.DateField(verbose_name='Fecha', db_index=True)
    note = models.TextField(blank=True, verbose_name='Nota')
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True, verbose_name='Comprobante')
    reserve = models.ForeignKey('goals.Reserve', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Reserva')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-date', '-created_at']

    def __str__(self):
        sign = '+' if self.type == 'INCOME' else '-'
        return f'{sign}${self.amount} — {self.category} ({self.date.strftime("%d/%m")})'
