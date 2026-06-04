from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    class Cycle(models.TextChoices):
        WEEKLY = 'WEEKLY', 'Semanal'
        MONTHLY = 'MONTHLY', 'Mensual'
        YEARLY = 'YEARLY', 'Anual'

    name = models.CharField(max_length=200, verbose_name='Nombre')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    cycle = models.CharField(max_length=10, choices=Cycle.choices, default=Cycle.MONTHLY, verbose_name='Ciclo')
    next_date = models.DateField(verbose_name='Próximo cobro')
    category = models.ForeignKey('finances.Category', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Categoría')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        ordering = ['next_date', 'name']

    def __str__(self):
        return f'{self.name} — {self.currency.symbol}{self.amount}/{self.get_cycle_display().lower()}'

    def monthly_cost(self):
        if self.cycle == 'WEEKLY':
            return float(self.amount) * 4.33
        elif self.cycle == 'MONTHLY':
            return float(self.amount)
        elif self.cycle == 'YEARLY':
            return float(self.amount) / 12
        return float(self.amount)

    def days_until_next(self):
        delta = self.next_date - timezone.now().date()
        return delta.days
