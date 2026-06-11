from django.contrib import admin
from .models import Goal


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_amount', 'current_amount', 'progress_pct', 'deadline', 'is_achieved', 'colony']
    list_filter = ['is_achieved', 'deadline', 'colony']
    search_fields = ['name']
