from django.db import models
from django.db.models import Sum, Subquery, OuterRef
from django.utils import timezone


class BudgetQuerySet(models.QuerySet):
    def with_spent(self):
        from finances.models import Transaction
        spent_subquery = Transaction.objects.filter(
            category=OuterRef('category'),
            colony=OuterRef('colony'),
            type='EXPENSE',
            date__year=OuterRef('year'),
            date__month=OuterRef('month'),
            currency=OuterRef('currency'),
        ).order_by().values('category').annotate(
            total=Sum('amount')
        ).values('total')[:1]
        return self.annotate(_spent_total=Subquery(spent_subquery))


class Budget(models.Model):
    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia')
    category = models.ForeignKey('finances.Category', on_delete=models.CASCADE, verbose_name='Categoría',
                                 limit_choices_to={'type': 'EXPENSE'})
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Límite mensual')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    month = models.IntegerField(verbose_name='Mes')
    year = models.IntegerField(verbose_name='Año')

    objects = BudgetQuerySet.as_manager()

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-year', '-month', 'category__name']
        unique_together = ['colony', 'category', 'month', 'year']

    def __str__(self):
        return f'{self.category.name} — {self.currency.symbol}{self.limit_amount} ({self.month}/{self.year})'

    def spent(self):
        if hasattr(self, '_spent_total') and self._spent_total is not None:
            return self._spent_total
        return self.category.transaction_set.filter(
            colony=self.colony,
            type='EXPENSE',
            date__year=self.year,
            date__month=self.month,
            currency=self.currency,
        ).aggregate(s=Sum('amount'))['s'] or 0

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
