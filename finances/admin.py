from django.contrib import admin
from .models import Currency, Category, Tag, Transaction


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'symbol', 'name', 'rate_to_base']
    list_editable = ['rate_to_base']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'icon', 'color']
    list_filter = ['type']
    list_editable = ['type', 'icon', 'color']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'amount', 'currency', 'category', 'note']
    list_filter = ['type', 'category', 'date']
    search_fields = ['note', 'custom_tags']
    date_hierarchy = 'date'
