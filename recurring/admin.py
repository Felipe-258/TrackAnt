from django.contrib import admin
from .models import RecurringTransaction


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'currency', 'cycle', 'next_date', 'is_active']
    list_filter = ['is_active', 'cycle']
    search_fields = ['name', 'note']
