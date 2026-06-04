from django import forms
from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit_amount', 'currency', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'limit_amount': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'step': '0.01',
                'placeholder': '0.00',
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'month': forms.Select(choices=[(i, ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'][i-1]) for i in range(1,13)], attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'year': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'min': 2020,
                'max': 2035,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = self.fields['category'].queryset.filter(type='EXPENSE')
