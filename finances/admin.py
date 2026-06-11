from django.contrib import admin
from .models import Currency, Category, Tag, Transaction


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'symbol', 'name', 'rate_to_base', 'colony']
    list_editable = ['rate_to_base']
    list_filter = ['colony']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'icon', 'color', 'colony']
    list_filter = ['type', 'colony']
    list_editable = ['type', 'icon', 'color']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'colony']
    search_fields = ['name']
    list_filter = ['colony']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'amount', 'currency', 'category', 'colony', 'note']
    list_filter = ['type', 'category', 'date', 'colony']
    search_fields = ['note', 'custom_tags']
    date_hierarchy = 'date'
