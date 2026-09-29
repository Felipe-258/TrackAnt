from django import forms
from django.db.models import Q
from .models import InstallmentPurchase


class InstallmentPurchaseForm(forms.ModelForm):
    class Meta:
        model = InstallmentPurchase
        fields = ['name', 'total_amount', 'installment_amount', 'installments_count', 'currency', 'category', 'start_date', 'auto_debit', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500', 'placeholder': 'Ej: TV Samsung, Notebook...'}),
            'total_amount': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'step': '0.01', 'inputmode': 'decimal'}),
            'installment_amount': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'step': '0.01', 'placeholder': 'Automático si se deja vacío', 'inputmode': 'decimal'}),
            'installments_count': forms.NumberInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'min': '1', 'inputmode': 'numeric'}),
            'currency': forms.Select(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200', 'type': 'date'}),
            'auto_debit': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-earth-300 text-gold-600 focus:ring-gold-500 dark:border-earth-600 dark:bg-earth-800'}),
            'note': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500', 'rows': 3, 'placeholder': 'Nota opcional...'}),
        }

    def __init__(self, *args, colony=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].empty_label = None
        if colony:
            from finances.models import Currency, Category
            colony_filter = Q(colony=colony) | Q(colony__isnull=True)
            self.fields['category'].queryset = Category.objects.filter(colony_filter, type='EXPENSE')
            self.fields['currency'].queryset = Currency.objects.filter(colony_filter)

    def clean(self):
        from decimal import Decimal
        cleaned = super().clean()
        total = cleaned.get('total_amount')
        count = cleaned.get('installments_count')
        inst_amt = cleaned.get('installment_amount')

        if total and count:
            calculated = (total / count).quantize(Decimal('0.01'))
            if not inst_amt or inst_amt == 0:
                cleaned['installment_amount'] = calculated
        return cleaned
