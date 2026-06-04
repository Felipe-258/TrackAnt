from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'limit_amount', 'currency', 'month', 'year', 'spent', 'status']
    list_filter = ['month', 'year', 'category']
