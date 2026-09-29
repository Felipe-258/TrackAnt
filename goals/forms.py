from django import forms
from django.db.models import Q
from .models import Reserve


class ReserveForm(forms.ModelForm):
    class Meta:
        model = Reserve
        fields = ['name', 'target_amount', 'currency', 'deadline', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
                'placeholder': 'Ej: Fondo de emergencia, Inversión...',
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'step': '0.01',
                'placeholder': '0.00',
                'inputmode': 'decimal',
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'type': 'date',
            }, format='%Y-%m-%d'),
            'color': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'type': 'color',
            }),
        }

    def __init__(self, *args, colony=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].empty_label = None
        self.fields['target_amount'].required = False
        if colony:
            from finances.models import Currency
            colony_filter = Q(colony=colony) | Q(colony__isnull=True)
            self.fields['currency'].queryset = Currency.objects.filter(colony_filter)
