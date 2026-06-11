from datetime import date

from django.db import models


class Goal(models.Model):
    colony = models.ForeignKey('users.Colony', on_delete=models.CASCADE, verbose_name='Colonia')
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

    def time_until_deadline(self):
        if not self.deadline or self.is_achieved:
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
