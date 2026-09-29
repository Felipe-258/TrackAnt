from django.db import models

from trackant.utils import time_until_deadline as _time_until_deadline


class Reserve(models.Model):
    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Monto objetivo')
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Saldo actual')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    deadline = models.DateField(blank=True, null=True, verbose_name='Fecha límite')
    color = models.CharField(max_length=7, default='#C4943A', verbose_name='Color')
    is_achieved = models.BooleanField(default=False, verbose_name='Alcanzada')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-is_achieved', 'deadline', 'name']

    def __str__(self):
        if self.target_amount is not None:
            return f'{self.name} — ${self.current_amount}/${self.target_amount}'
        return f'{self.name} — ${self.current_amount}'

    @property
    def has_target(self):
        return self.target_amount is not None

    def progress_pct(self):
        if self.target_amount is None or self.target_amount <= 0:
            return None
        return min(int(self.current_amount / self.target_amount * 100), 100)

    def remaining(self):
        if self.target_amount is None:
            return None
        remaining = self.target_amount - self.current_amount
        return max(remaining, 0)

    def time_until_deadline(self):
        return _time_until_deadline(self.deadline, self.is_achieved)
