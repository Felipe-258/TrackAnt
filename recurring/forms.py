from django import forms
from django.db.models import Q
from .models import RecurringTransaction


class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = ['name', 'amount', 'currency', 'category', 'cycle', 'day_of_month', 'day_of_week', 'start_date', 'end_date', 'note', 'is_active', 'next_date']
        widgets = {
            'next_date': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500', 'placeholder': 'Ej: Alquiler, Expensas...'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200'}),
            'cycle': forms.Select(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'x-on:change': 'cycleChanged($event)'}),
            'day_of_month': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'min': '1', 'max': '31', 'placeholder': '15'}),
            'day_of_week': forms.Select(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-earth-300 text-gold-600 focus:ring-gold-500 dark:border-earth-600 dark:bg-earth-800'}),
        }
        DAY_OF_WEEK_CHOICES = [(None, '---')] + [(i, dia) for i, dia in enumerate(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'], 1)]

    def __init__(self, *args, colony=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['next_date'].required = False
        self.fields['currency'].empty_label = None
        self.fields['day_of_week'].widget = forms.Select(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200'})
        self.fields['day_of_week'].choices = [(None, '---')] + [(i, d) for i, d in enumerate(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'], 1)]
        self.fields['day_of_week'].required = False
        if colony:
            from finances.models import Currency, Category
            colony_filter = Q(colony=colony) | Q(colony__isnull=True)
            self.fields['category'].queryset = Category.objects.filter(colony_filter, type='EXPENSE')
            self.fields['currency'].queryset = Currency.objects.filter(colony_filter)

    def clean(self):
        cleaned = super().clean()
        cycle = cleaned.get('cycle')
        dom = cleaned.get('day_of_month')
        dow = cleaned.get('day_of_week')
        end = cleaned.get('end_date')

        if cycle in ['WEEKLY', 'BIWEEKLY'] and not dow:
            self.add_error('day_of_week', 'Requerido para ciclo semanal/quincenal')
        if cycle in ['MONTHLY', 'BIMONTHLY'] and not dom:
            self.add_error('day_of_month', 'Requerido para ciclo mensual/bimestral')

        sd = cleaned.get('start_date')
        if sd and (dom or dow or cycle):
            from datetime import timedelta
            from dateutil.relativedelta import relativedelta
            from django.utils import timezone
            from trackant.utils import cap_day
            today = timezone.now().date()

            if dom:
                d = date(sd.year, sd.month, cap_day(sd.year, sd.month, dom))
            elif dow:
                d = sd + timedelta(days=(dow - sd.isoweekday()) % 7)
            else:
                d = sd

            while d <= today:
                if cycle == 'WEEKLY':
                    d += timedelta(weeks=1)
                elif cycle == 'BIWEEKLY':
                    d += timedelta(weeks=2)
                elif cycle == 'MONTHLY':
                    d += relativedelta(months=1)
                elif cycle == 'BIMONTHLY':
                    d += relativedelta(months=2)
                elif cycle == 'YEARLY':
                    d += relativedelta(years=1)
                else:
                    break

            if end and d > end:
                self.add_error('end_date', 'El gasto recurrente ya finalizó (próxima ocurrencia después de la fecha de fin)')
            cleaned['next_date'] = d

        return cleaned
