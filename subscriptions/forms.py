from django import forms
from django.db.models import Q
from .models import Subscription


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'amount', 'currency', 'cycle', 'next_date', 'category', 'auto_debit', 'is_variable', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
                'placeholder': 'Ej: Netflix, Spotify, Gimnasio...',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'step': '0.01',
                'inputmode': 'decimal',
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'cycle': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'next_date': forms.DateInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'type': 'date',
            }, format='%Y-%m-%d'),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'auto_debit': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-earth-300 text-gold-600 focus:ring-gold-500 dark:border-earth-600 dark:bg-earth-800',
            }),
            'is_variable': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-earth-300 text-gold-600 focus:ring-gold-500 dark:border-earth-600 dark:bg-earth-800',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-earth-300 text-gold-600 focus:ring-gold-500 dark:border-earth-600 dark:bg-earth-800',
            }),
        }

    def __init__(self, *args, colony=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].empty_label = None
        self.fields['amount'].label = 'Monto estimado'
        self.fields['amount'].help_text = 'Referencia. Si es variable, se pide el monto real al pagar.'
        if colony:
            from finances.models import Currency, Category
            colony_filter = Q(colony=colony) | Q(colony__isnull=True)
            self.fields['category'].queryset = Category.objects.filter(colony_filter, type='EXPENSE')
            self.fields['currency'].queryset = Currency.objects.filter(colony_filter)
        else:
            from finances.models import Category
            self.fields['category'].queryset = Category.objects.filter(type='EXPENSE')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.is_variable:
            instance.auto_debit = False
        if commit:
            instance.save()
        return instance
