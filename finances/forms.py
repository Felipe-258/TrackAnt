from django import forms
from django.db.models import Q
from .models import Transaction, Category
from goals.models import Reserve


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'currency', 'category', 'reserve', 'date', 'note', 'receipt']
        widgets = {
            'type': forms.RadioSelect(attrs={
                'class': 'peer sr-only',
                'hx-get': '/transactions/category-options/',
                'hx-target': '#category-field',
                'hx-trigger': 'change',
                'hx-swap': 'innerHTML',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full min-w-0 box-border rounded-lg border border-earth-300 bg-white px-4 py-3 text-base text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500 sm:text-sm sm:py-2.5',
                'step': '0.01',
                'placeholder': '0.00',
                'inputmode': 'decimal',
                'enterkeyhint': 'done',
                'autocomplete': 'off',
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-3 text-base text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 sm:text-sm sm:py-2.5',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-3 text-base text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500 sm:text-sm sm:py-2.5',
                'type': 'date',
                'inputmode': 'none',
            }, format='%Y-%m-%d'),
            'note': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-3 text-base text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500 sm:text-sm sm:py-2.5',
                'rows': 3,
                'placeholder': 'Agrega una nota opcional...',
                'inputmode': 'text',
                'enterkeyhint': 'done',
                'autocapitalize': 'sentences',
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'w-full text-base text-earth-500 file:mr-3 file:rounded-lg file:border-0 file:bg-clay-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-clay-700 hover:file:bg-clay-100 dark:file:bg-clay-900/30 dark:file:text-clay-300 sm:text-sm',
            }),
            'reserve': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
        }

    def __init__(self, *args, colony=None, **kwargs):
        self.colony = colony
        super().__init__(*args, **kwargs)
        self.fields['type'].empty_label = None
        self.fields['currency'].empty_label = None
        self.fields['category'].empty_label = None
        self.fields['reserve'].empty_label = 'Sin reserva'
        type_val = self.initial.get('type')
        if self.data.get('type'):
            type_val = self.data.get('type')
        colony_filter = Q(colony=colony) | Q(colony__isnull=True) if colony else Q(colony__isnull=True)
        if type_val:
            self.fields['category'].queryset = Category.objects.filter(colony_filter, type=type_val)
        else:
            self.fields['category'].queryset = Category.objects.filter(colony_filter, type='EXPENSE')
        if colony:
            from .models import Currency
            self.fields['currency'].queryset = Currency.objects.filter(colony_filter)
            self.fields['reserve'].queryset = Reserve.objects.filter(colony=colony, is_achieved=False, target_amount__isnull=False).select_related('currency')

    def save(self, commit=True):
        instance = super().save(commit=commit)
        return instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'placeholder': 'Nombre de la categoría',
            }),
            'type': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'placeholder': 'Nombre del icono Lucide (ej: wallet)',
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'type': 'color',
            }),
        }
