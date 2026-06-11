from django.contrib import admin
from .models import SplitGroup, SplitExpense


class SplitExpenseInline(admin.TabularInline):
    model = SplitExpense
    extra = 0


@admin.register(SplitGroup)
class SplitGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'members', 'total_spent', 'created_at', 'colony']
    list_filter = ['colony']
    inlines = [SplitExpenseInline]
