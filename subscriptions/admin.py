from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'currency', 'cycle', 'next_date', 'is_active', 'days_until_next']
    list_filter = ['is_active', 'cycle', 'next_date']
    search_fields = ['name']
