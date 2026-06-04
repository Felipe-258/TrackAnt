from django.contrib import admin
from .models import Debt, DebtPayment


class DebtPaymentInline(admin.TabularInline):
    model = DebtPayment
    extra = 0


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['person', 'amount', 'debt_type', 'currency', 'date', 'is_settled', 'remaining']
    list_filter = ['debt_type', 'is_settled', 'date']
    search_fields = ['person', 'note']
    inlines = [DebtPaymentInline]
