from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Q
from datetime import date

from finances.models import Transaction, Category
from goals.models import Goal
from debts.models import Debt
from subscriptions.models import Subscription


@api_view(['GET'])
def api_stats(request):
    today = date.today()
    month_transactions = Transaction.objects.filter(date__year=today.year, date__month=today.month)
    monthly_income = float(month_transactions.filter(type='INCOME').aggregate(s=Sum('amount'))['s'] or 0)
    monthly_expenses = float(month_transactions.filter(type='EXPENSE').aggregate(s=Sum('amount'))['s'] or 0)
    total = Transaction.objects.aggregate(
        i=Sum('amount', filter=Q(type='INCOME')),
        e=Sum('amount', filter=Q(type='EXPENSE')),
    )
    balance = float((total['i'] or 0) - (total['e'] or 0))

    return Response({
        'balance': balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'goals_count': Goal.objects.filter(is_achieved=False).count(),
        'debts_owe_count': Debt.objects.filter(debt_type='OWE', is_settled=False).count(),
        'debts_owed_count': Debt.objects.filter(debt_type='OWED', is_settled=False).count(),
        'active_subscriptions': Subscription.objects.filter(is_active=True).count(),
    })


@api_view(['GET'])
def api_stats_by_category(request):
    today = date.today()
    expenses = Transaction.objects.filter(
        type='EXPENSE',
        date__year=today.year,
        date__month=today.month,
    ).values('category__name', 'category__icon', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')

    return Response([
        {
            'name': e['category__name'],
            'icon': e['category__icon'],
            'color': e['category__color'],
            'total': float(e['total']),
        }
        for e in expenses
    ])


@api_view(['GET'])
def api_stats_monthly(request):
    today = date.today()
    data = []
    for m in range(1, today.month + 1):
        income = float(Transaction.objects.filter(
            type='INCOME', date__year=today.year, date__month=m
        ).aggregate(s=Sum('amount'))['s'] or 0)
        expense = float(Transaction.objects.filter(
            type='EXPENSE', date__year=today.year, date__month=m
        ).aggregate(s=Sum('amount'))['s'] or 0)
        data.append({'month': m, 'income': income, 'expense': expense})
    return Response(data)


urlpatterns = [
    path('', include('finances.api_urls')),
    path('', include('goals.api_urls')),
    path('', include('debts.api_urls')),
    path('', include('budgets.api_urls')),
    path('', include('subscriptions.api_urls')),
    path('', include('splits.api_urls')),
    path('stats/', api_stats, name='api-stats'),
    path('stats/by-category/', api_stats_by_category, name='api-stats-category'),
    path('stats/monthly/', api_stats_monthly, name='api-stats-monthly'),
]
