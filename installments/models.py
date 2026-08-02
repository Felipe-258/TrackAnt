from django.db import models


class InstallmentPurchase(models.Model):
    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia', db_index=True)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto total')
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Monto por cuota', help_text='Dejar vacío para calcular automático')
    installments_count = models.PositiveIntegerField(verbose_name='Cantidad de cuotas')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    category = models.ForeignKey('finances.Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Categoría')
    start_date = models.DateField(verbose_name='Fecha de inicio')
    auto_debit = models.BooleanField(default=True, verbose_name='Débito automático')
    is_completed = models.BooleanField(default=False, verbose_name='Completada', db_index=True)
    note = models.TextField(blank=True, verbose_name='Nota')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Compra en cuotas'
        verbose_name_plural = 'Compras en cuotas'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} ({self.installments_count} cuotas) — {self.currency.symbol}{self.total_amount}'

    def paid_count(self):
        return self.installments.filter(is_paid=True).count()

    def remaining_count(self):
        return self.installments.filter(is_paid=False).count()

    def paid_total(self):
        from django.db.models import Sum
        result = self.installments.filter(is_paid=True).aggregate(t=Sum('amount'))['t']
        return result or 0

    def progress_pct(self):
        if self.installments_count == 0:
            return 0
        return int(self.paid_count() / self.installments_count * 100)


class Installment(models.Model):
    purchase = models.ForeignKey(InstallmentPurchase, on_delete=models.CASCADE, related_name='installments', verbose_name='Compra')
    number = models.PositiveIntegerField(verbose_name='Número de cuota')
    due_date = models.DateField(verbose_name='Fecha de vencimiento', db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    is_paid = models.BooleanField(default=False, verbose_name='Pagada', db_index=True)
    paid_date = models.DateField(null=True, blank=True, verbose_name='Fecha de pago')
    transaction = models.ForeignKey('finances.Transaction', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Transacción')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'
        ordering = ['due_date', 'number']
        unique_together = [('purchase', 'number')]

    def __str__(self):
        status = 'Pagada' if self.is_paid else 'Pendiente'
        return f'{self.purchase.name} — Cuota {self.number}/{self.purchase.installments_count} ({status})'
