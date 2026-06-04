from django import forms
from .models import SplitGroup, SplitExpense


class SplitGroupForm(forms.ModelForm):
    members_list = forms.CharField(
        label='Miembros',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
            'placeholder': 'Juan, María, Pedro...',
        }),
        help_text='Nombres separados por coma',
    )

    class Meta:
        model = SplitGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
                'placeholder': 'Ej: Viaje a la costa',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.members:
            self.fields['members_list'].initial = ', '.join(self.instance.members)

    def clean_members_list(self):
        raw = self.cleaned_data['members_list']
        members = [m.strip() for m in raw.split(',') if m.strip()]
        if not members:
            raise forms.ValidationError('Al menos un miembro es requerido')
        return members

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.members = self.cleaned_data['members_list']
        if commit:
            instance.save()
        return instance


class SplitExpenseForm(forms.ModelForm):
    class Meta:
        model = SplitExpense
        fields = ['description', 'amount', 'currency', 'paid_by', 'date']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
                'placeholder': 'Ej: Cena, Taxi, Entradas...',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'step': '0.01',
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'paid_by': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if group:
            choices = [(m, m) for m in group.members]
            self.fields['paid_by'] = forms.ChoiceField(choices=choices, widget=forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }))
