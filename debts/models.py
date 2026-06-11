from datetime import date

from django.db import models


class Debt(models.Model):
    class Type(models.TextChoices):
        OWE = 'OWE', 'Yo debo'
        OWED = 'OWED', 'Me deben'

    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia')
    person = models.CharField(max_length=200, verbose_name='Persona')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto total')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    debt_type = models.CharField(max_length=4, choices=Type.choices, verbose_name='Tipo')
    date = models.DateField(verbose_name='Fecha')
    deadline = models.DateField(blank=True, null=True, verbose_name='Fecha límite')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Interés anual %')
    note = models.TextField(blank=True, verbose_name='Nota')
    is_settled = models.BooleanField(default=False, verbose_name='Saldada')
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
        if not self.deadline or self.is_settled:
            return None
        days = (self.deadline - date.today()).days
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
