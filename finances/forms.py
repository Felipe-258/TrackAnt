from django import forms
from django.db.models import Q
from .models import Transaction, Category, Tag
from goals.models import Goal


class TransactionForm(forms.ModelForm):
    tag_names = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='Etiquetas',
    )
    new_tags = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='Nuevas etiquetas',
    )

    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'currency', 'category', 'goal', 'date', 'note', 'receipt', 'is_recurring', 'tag_names', 'new_tags']
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
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-earth-300 text-clay-600 focus:ring-clay-500 dark:border-earth-600 dark:bg-earth-800',
            }),
            'goal': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
        }

    def __init__(self, *args, colony=None, **kwargs):
        self.colony = colony
        super().__init__(*args, **kwargs)
        self.fields['type'].empty_label = None
        self.fields['currency'].empty_label = None
        self.fields['category'].empty_label = None
        self.fields['goal'].empty_label = 'Sin meta'
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
            self.fields['goal'].queryset = Goal.objects.filter(colony=colony, is_achieved=False).select_related('currency')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

        tag_ids = self.cleaned_data.get('tag_names', '')
        new_tags_raw = self.cleaned_data.get('new_tags', '')

        if tag_ids:
            ids = [int(i) for i in tag_ids.split(',') if i.isdigit()]
            tag_filter = Q(colony=self.colony) | Q(colony__isnull=True) if self.colony else Q(colony__isnull=True)
            instance.tags.set(Tag.objects.filter(tag_filter, id__in=ids))

        if new_tags_raw:
            existing = [t.strip() for t in new_tags_raw.split(',') if t.strip()]
            current_json = instance.custom_tags or []
            for tag_name in existing:
                if tag_name not in current_json:
                    current_json.append(tag_name)
            instance.custom_tags = current_json

        if commit:
            instance.save()

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
