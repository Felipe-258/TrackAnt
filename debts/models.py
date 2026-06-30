from django.db import models

from trackant.utils import time_until_deadline as _time_until_deadline


class Debt(models.Model):
    class Type(models.TextChoices):
        OWE = 'OWE', 'Yo debo'
        OWED = 'OWED', 'Me deben'

    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia', db_index=True)
    person = models.CharField(max_length=200, verbose_name='Persona')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto total')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    debt_type = models.CharField(max_length=4, choices=Type.choices, verbose_name='Tipo')
    date = models.DateField(verbose_name='Fecha')
    deadline = models.DateField(blank=True, null=True, verbose_name='Fecha límite')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Interés anual %')
    note = models.TextField(blank=True, verbose_name='Nota')
    is_settled = models.BooleanField(default=False, verbose_name='Saldada', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Deuda'
        verbose_name_plural = 'Deudas'
        ordering = ['is_settled', '-date']

    def __str__(self):
        return f'{self.person} — {self.currency.symbol}{self.amount}'

    def paid_total(self):
        return self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0

    def remaining(self):
        return max(self.amount - self.paid_total(), 0)

    def progress_pct(self):
        if self.amount <= 0:
            return 0
        return min(int(self.paid_total() / self.amount * 100), 100)

    def time_until_deadline(self):
        return _time_until_deadline(self.deadline, self.is_settled)


class DebtPayment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments', verbose_name='Deuda')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    date = models.DateField(verbose_name='Fecha')
    note = models.TextField(blank=True, verbose_name='Nota')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pago de deuda'
        verbose_name_plural = 'Pagos de deudas'
        ordering = ['-date']

    def __str__(self):
        return f'${self.amount} — {self.debt.person} ({self.date})'
