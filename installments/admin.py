from django.contrib import admin
from .models import InstallmentPurchase, Installment


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0
    readonly_fields = ['number', 'due_date', 'amount', 'is_paid', 'paid_date']


@admin.register(InstallmentPurchase)
class InstallmentPurchaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_amount', 'installments_count', 'currency', 'auto_debit', 'is_completed', 'start_date']
    list_filter = ['is_completed', 'auto_debit', 'currency']
    search_fields = ['name', 'note']
    inlines = [InstallmentInline]


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ['purchase', 'number', 'due_date', 'amount', 'is_paid']
    list_filter = ['is_paid']
