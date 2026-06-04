from django.db import models


class Goal(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto objetivo')
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Progreso actual')
    currency = models.ForeignKey('finances.Currency', on_delete=models.PROTECT, verbose_name='Moneda')
    deadline = models.DateField(blank=True, null=True, verbose_name='Fecha límite')
    color = models.CharField(max_length=7, default='#C4943A', verbose_name='Color')
    is_achieved = models.BooleanField(default=False, verbose_name='Alcanzada')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Meta'
        verbose_name_plural = 'Metas'
        ordering = ['-is_achieved', 'deadline', 'name']

    def __str__(self):
        return f'{self.name} — ${self.current_amount}/${self.target_amount}'

    def progress_pct(self):
        if self.target_amount <= 0:
            return 0
        return min(int(self.current_amount / self.target_amount * 100), 100)

    def remaining(self):
        remaining = self.target_amount - self.current_amount
        return max(remaining, 0)
