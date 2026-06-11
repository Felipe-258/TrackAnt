from django.db import models


class SplitGroup(models.Model):
    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    members = models.JSONField(default=list, verbose_name='Miembros')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def balance(self):
        expenses = self.expenses.all()
        balance = {}
        for m in self.members:
            balance[m] = 0
        for e in expenses:
            balance[e.paid_by] = balance.get(e.paid_by, 0) + float(e.amount)
            for person, share in e.shares.items():
                balance[person] = balance.get(person, 0) - share
        return balance

    def total_spent(self):
        return sum(float(e.amount) for e in self.expenses.all())


class SplitExpense(models.Model):
    group = models.ForeignKey(SplitGroup, on_delete=models.CASCADE, related_name='expenses', verbose_name='Grupo')
    description = models.CharField(max_length=200, verbose_name='Descripción')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto total')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    paid_by = models.CharField(max_length=200, verbose_name='Pagado por')
    date = models.DateField(verbose_name='Fecha')
    shares = models.JSONField(default=dict, verbose_name='División')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gasto compartido'
        verbose_name_plural = 'Gastos compartidos'
        ordering = ['-date']

    def __str__(self):
        return f'{self.description} — {self.currency.symbol}{self.amount}'
