from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Budget(models.Model):
    category = models.ForeignKey('finances.Category', on_delete=models.CASCADE, verbose_name='Categoría',
                                 limit_choices_to={'type': 'EXPENSE'})
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Límite mensual')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    month = models.IntegerField(verbose_name='Mes')
    year = models.IntegerField(verbose_name='Año')

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-year', '-month', 'category__name']
        unique_together = ['category', 'month', 'year']

    def __str__(self):
        return f'{self.category.name} — {self.currency.symbol}{self.limit_amount} ({self.month}/{self.year})'

    def spent(self):
        total = self.category.transaction_set.filter(
            type='EXPENSE',
            date__year=self.year,
            date__month=self.month,
            currency=self.currency,
        ).aggregate(s=Sum('amount'))['s'] or 0
        return total

    def remaining(self):
        return max(self.limit_amount - self.spent(), 0)

    def pct(self):
        if self.limit_amount <= 0:
            return 0
        spent = self.spent()
        return min(int(spent / self.limit_amount * 100), 100)

    def status(self):
        pct = self.pct()
        if pct >= 100:
            return 'danger'
        elif pct >= 80:
            return 'warning'
        elif pct >= 50:
            return 'caution'
        return 'ok'
