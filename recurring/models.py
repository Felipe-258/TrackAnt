from django.db import models
from django.utils import timezone


class RecurringTransaction(models.Model):
    class Cycle(models.TextChoices):
        WEEKLY = 'WEEKLY', 'Semanal'
        BIWEEKLY = 'BIWEEKLY', 'Quincenal'
        MONTHLY = 'MONTHLY', 'Mensual'
        BIMONTHLY = 'BIMONTHLY', 'Bimestral'
        YEARLY = 'YEARLY', 'Anual'

    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia', db_index=True)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    category = models.ForeignKey('finances.Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Categoría')
    cycle = models.CharField(max_length=10, choices=Cycle.choices, default=Cycle.MONTHLY, verbose_name='Ciclo')
    day_of_month = models.PositiveIntegerField(null=True, blank=True, verbose_name='Día del mes', help_text='1-31, solo para ciclo mensual/bimestral')
    day_of_week = models.PositiveIntegerField(null=True, blank=True, verbose_name='Día de la semana', help_text='1=Lun..7=Dom, solo para ciclo semanal/quincenal')
    next_date = models.DateField(verbose_name='Próximo cobro')
    start_date = models.DateField(verbose_name='Fecha de inicio')
    end_date = models.DateField(null=True, blank=True, verbose_name='Fecha de fin')
    note = models.TextField(blank=True, verbose_name='Nota', help_text='Se copiará a cada transacción generada')
    is_active = models.BooleanField(default=True, verbose_name='Activo', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Gasto recurrente'
        verbose_name_plural = 'Gastos recurrentes'
        ordering = ['next_date', 'name']

    def __str__(self):
        return f'{self.name} — {self.currency.symbol}{self.amount}/{self.get_cycle_display().lower()}'

    def next_occurrence(self):
        from dateutil.relativedelta import relativedelta
        from datetime import timedelta
        from trackant.utils import cap_day

        d = self.next_date
        if self.cycle == 'WEEKLY':
            return d + timedelta(weeks=1)
        elif self.cycle == 'BIWEEKLY':
            return d + timedelta(weeks=2)
        elif self.cycle == 'MONTHLY':
            n = d + relativedelta(months=1)
            if self.day_of_month:
                n = n.replace(day=cap_day(n.year, n.month, self.day_of_month))
            return n
        elif self.cycle == 'BIMONTHLY':
            n = d + relativedelta(months=2)
            if self.day_of_month:
                n = n.replace(day=cap_day(n.year, n.month, self.day_of_month))
            return n
        elif self.cycle == 'YEARLY':
            return d + relativedelta(years=1)
        return d

    def monthly_cost(self):
        if self.cycle == 'WEEKLY':
            return float(self.amount) * 4.33
        elif self.cycle == 'BIWEEKLY':
            return float(self.amount) * 2.17
        elif self.cycle == 'MONTHLY':
            return float(self.amount)
        elif self.cycle == 'BIMONTHLY':
            return float(self.amount) / 2
        elif self.cycle == 'YEARLY':
            return float(self.amount) / 12
        return float(self.amount)

    def days_until_next(self):
        delta = self.next_date - timezone.now().date()
        return delta.days

    def day_label(self):
        if self.day_of_month:
            return f'Día {self.day_of_month}'
        if self.day_of_week:
            days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            return days[self.day_of_week - 1]
        return ''

    def save(self, *args, **kwargs):
        if self.day_of_month and not self.next_date:
            from datetime import date
            from trackant.utils import cap_day
            self.next_date = date(self.start_date.year, self.start_date.month, cap_day(self.start_date.year, self.start_date.month, self.day_of_month))
        super().save(*args, **kwargs)
