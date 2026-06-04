from django import forms
from .models import Transaction, Category, Tag


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
        fields = ['type', 'amount', 'currency', 'category', 'date', 'note', 'receipt', 'is_recurring', 'tag_names', 'new_tags']
        widgets = {
            'type': forms.RadioSelect(attrs={
                'class': 'peer sr-only',
                'hx-get': '/transactions/category-options/',
                'hx-target': '#category-field',
                'hx-trigger': 'change',
                'hx-swap': 'innerHTML',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
                'step': '0.01',
                'placeholder': '0.00',
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'type': 'date',
            }),
            'note': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 placeholder-earth-400 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200 dark:placeholder-earth-500',
                'rows': 2,
                'placeholder': 'Agregá una nota opcional...',
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'w-full text-sm text-earth-500 file:mr-3 file:rounded-lg file:border-0 file:bg-clay-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-clay-700 hover:file:bg-clay-100 dark:file:bg-clay-900/30 dark:file:text-clay-300',
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-earth-300 text-clay-600 focus:ring-clay-500 dark:border-earth-600 dark:bg-earth-800',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].empty_label = None
        type_val = self.initial.get('type')
        if self.data.get('type'):
            type_val = self.data.get('type')
        if type_val:
            self.fields['category'].queryset = Category.objects.filter(type=type_val)
        else:
            self.fields['category'].queryset = Category.objects.filter(type='EXPENSE')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

        tag_ids = self.cleaned_data.get('tag_names', '')
        new_tags_raw = self.cleaned_data.get('new_tags', '')

        if tag_ids:
            ids = [int(i) for i in tag_ids.split(',') if i.isdigit()]
            instance.tags.set(Tag.objects.filter(id__in=ids))

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
                'placeholder': '🛒',
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-earth-300 bg-white px-4 py-2.5 text-sm text-earth-900 focus:border-clay-400 focus:outline-none focus:ring-2 focus:ring-clay-400/20 dark:border-earth-700 dark:bg-earth-800 dark:text-earth-200',
                'type': 'color',
            }),
        }
