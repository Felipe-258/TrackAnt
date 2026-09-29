from decimal import Decimal

from django.db import models


class SplitGroup(models.Model):
    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    members = models.JSONField(default=list, verbose_name='Miembros')
    payment_preferences = models.JSONField(default=dict, verbose_name='Preferencias de pago')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def balance_by_currency(self):
        """{currency_code: {persona: saldo_neto Decimal}}. Positivo = le deben, negativo = debe."""
        balance = {}
        for e in self.expenses.select_related('currency').all():
            code = e.currency.code
            if code not in balance:
                balance[code] = {m: Decimal('0') for m in self.members}
            balance[code][e.paid_by] = balance[code].get(e.paid_by, Decimal('0')) + e.amount
            for person, share in e.shares.items():
                if person not in balance[code]:
                    balance[code][person] = Decimal('0')
                balance[code][person] = balance[code][person] - Decimal(str(share))
        # aplico pagos internos
        for p in self.payments.select_related('currency').all():
            code = p.currency.code
            if code not in balance:
                balance[code] = {m: Decimal('0') for m in self.members}
            balance[code][p.payer] = balance[code].get(p.payer, Decimal('0')) + p.amount
            balance[code][p.payee] = balance[code].get(p.payee, Decimal('0')) - p.amount
        return balance

    def settle_debts(self):
        """Pares de deuda minima con preferencias suaves: [{payer, payee, amount, currency_code}]."""
        results = []
        for code, net in self.balance_by_currency().items():
            # copia mutable por persona, solo miembros presentes
            owed = {m: net.get(m, Decimal('0')) for m in self.members}
            prefs = dict(self.payment_preferences or {})

            # paso preferencias: payer debe -> si su preferido es acreedor, transferir
            for payer, payee in prefs.items():
                if payer not in owed or payee not in owed or payer == payee:
                    continue
                while owed[payer] < 0 and owed[payee] > 0:
                    amount = min(-owed[payer], owed[payee])
                    if amount <= 0:
                        break
                    results.append({'payer': payer, 'payee': payee, 'amount': amount, 'currency_code': code})
                    owed[payer] += amount
                    owed[payee] -= amount

            # greedy normal: deudor mas negativo -> acreedor mas positivo
            debtors = sorted([(m, -v) for m, v in owed.items() if v < 0], key=lambda x: -x[1])
            creditors = sorted([(m, v) for m, v in owed.items() if v > 0], key=lambda x: -x[1])
            i = j = 0
            while i < len(debtors) and j < len(creditors):
                debtor, d_amt = debtors[i]
                creditor, c_amt = creditors[j]
                if debtor == creditor:
                    if d_amt >= c_amt:
                        i += 1
                    else:
                        j += 1
                    continue
                amount = min(d_amt, c_amt)
                results.append({'payer': debtor, 'payee': creditor, 'amount': amount, 'currency_code': code})
                debtors[i] = (debtor, d_amt - amount)
                creditors[j] = (creditor, c_amt - amount)
                if debtors[i][1] == 0:
                    i += 1
                if creditors[j][1] == 0:
                    j += 1
        return results

    def total_spent(self):
        return sum(float(e.amount) for e in self.expenses.all())


class SplitPayment(models.Model):
    group = models.ForeignKey(SplitGroup, on_delete=models.CASCADE, related_name='payments', verbose_name='Grupo')
    payer = models.CharField(max_length=200, verbose_name='Pagó')
    payee = models.CharField(max_length=200, verbose_name='Recibió')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    date = models.DateField(verbose_name='Fecha')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pago de deuda'
        verbose_name_plural = 'Pagos de deudas'
        ordering = ['-date']

    def __str__(self):
        return f'{self.payer} → {self.payee} — {self.currency.symbol}{self.amount}'


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
