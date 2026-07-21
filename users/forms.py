from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser, Colony
from django.db.models import Q


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
        'placeholder': 'tu@email.com',
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
            'placeholder': 'Nombre de usuario',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
            'placeholder': 'Contrasena',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-gold-400 focus:outline-none focus:ring-2 focus:ring-gold-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
            'placeholder': 'Repeti la contrasena',
        })


class ColonySettingsForm(forms.ModelForm):
    class Meta:
        model = Colony
        fields = ['name', 'default_currency', 'auto_create_debt_transactions', 'auto_create_split_transactions', 'budget_alert_threshold']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
                'placeholder': 'Nombre de la colonia',
            }),
            'default_currency': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'auto_create_debt_transactions': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-earth-300 text-clay-600 focus:ring-clay-500 dark:border-earth-600 dark:bg-earth-800',
            }),
            'auto_create_split_transactions': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-earth-300 text-clay-600 focus:ring-clay-500 dark:border-earth-600 dark:bg-earth-800',
            }),
            'budget_alert_threshold': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'min': '50',
                'max': '100',
            }),
        }

    def __init__(self, *args, colony=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['default_currency'].empty_label = 'Sin moneda por defecto'
        if colony:
            colony_filter = Q(colony=colony) | Q(colony__isnull=True)
            from finances.models import Currency
            self.fields['default_currency'].queryset = Currency.objects.filter(colony_filter)
