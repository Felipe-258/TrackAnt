from django.contrib import admin
from .models import Subscription, SubscriptionPayment


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'currency', 'cycle', 'next_date', 'is_active', 'days_until_next', 'colony']
    list_filter = ['is_active', 'cycle', 'next_date', 'colony']
    search_fields = ['name']


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'due_date', 'is_paid', 'paid_date', 'transaction']
    list_filter = ['is_paid', 'due_date']
    search_fields = ['subscription__name']
