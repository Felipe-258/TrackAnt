from django.contrib import admin
from .models import Debt, DebtPayment


class DebtPaymentInline(admin.TabularInline):
    model = DebtPayment
    extra = 0


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['person', 'amount', 'debt_type', 'currency', 'date', 'deadline', 'is_settled', 'remaining', 'colony']
    list_filter = ['debt_type', 'is_settled', 'date', 'colony']
    search_fields = ['person', 'note']
    inlines = [DebtPaymentInline]
