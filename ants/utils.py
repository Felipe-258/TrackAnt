from datetime import date
from django.db.models import Sum, Q
from finances.models import Transaction
from goals.models import Goal
from budgets.models import Budget


def get_colony_state(goal_id=None):
    today = date.today()
    year, month = today.year, today.month

    month_qs = Transaction.objects.filter(date__year=year, date__month=month)
    monthly_income = float(month_qs.filter(type='INCOME').aggregate(s=Sum('amount'))['s'] or 0)
    monthly_expenses = float(month_qs.filter(type='EXPENSE').aggregate(s=Sum('amount'))['s'] or 0)

    total = Transaction.objects.aggregate(
        i=Sum('amount', filter=Q(type='INCOME')),
        e=Sum('amount', filter=Q(type='EXPENSE')),
    )
    total_balance = float((total['i'] or 0) - (total['e'] or 0))

    transaction_count = Transaction.objects.count()
    active_goals = Goal.objects.filter(is_achieved=False).count()

    if goal_id:
        main_goal = Goal.objects.filter(id=goal_id, is_achieved=False).first()
    if not goal_id or not main_goal:
        main_goal = Goal.objects.filter(is_achieved=False).first()

    goal_progress = main_goal.progress_pct() if main_goal else 0
    goal_color = main_goal.color if main_goal else '#C4943A'

    over_budget = Budget.objects.filter(
        month=month, year=year
    ).select_related('category').all()
    budget_alerts = sum(1 for b in over_budget if b.pct() >= 80)

    worker_ants = min(transaction_count, 12)
    soldier_ants = min(budget_alerts, 4)

    # Build leaf colors array
    recent = list(Transaction.objects.order_by('-date')[:worker_ants])
    leaf_colors = ['#6E8F4C' if t.type == 'INCOME' else '#D4764A' for t in recent]

    weather = _get_weather(monthly_income, monthly_expenses)
    queen_size = _queen_size(goal_progress)

    # Leaf pile: proportional to goal progress
    leaf_total = max(2, int(goal_progress / 6.25)) if goal_progress > 0 else 2
    leaf_brown = min(leaf_total, 14)
    leaf_green = max(0, int(leaf_total * 0.35))

    return {
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'worker_ants': worker_ants,
        'soldier_ants': soldier_ants,
        'weather': weather,
        'queen_size': queen_size,
        'queen_progress': goal_progress,
        'active_goals': active_goals,
        'transaction_count': transaction_count,
        'goal_name': main_goal.name if main_goal else None,
        'goal_currency': str(main_goal.currency.symbol) if main_goal else '',
        'goal_current': float(main_goal.current_amount) if main_goal else 0,
        'goal_target': float(main_goal.target_amount) if main_goal else 0,
        'goal_color': goal_color,
        'leaf_colors': leaf_colors,
        'leaf_brown_count': leaf_brown,
        'leaf_green_count': leaf_green,
    }


def _get_weather(income, expenses):
    if income == 0 and expenses == 0:
        return 'clear'
    if income >= expenses * 1.5:
        return 'sunny'
    elif income >= expenses:
        return 'cloudy'
    elif expenses == 0 and income > 0:
        return 'sunny'
    elif income >= expenses * 0.5:
        return 'rainy'
    else:
        return 'stormy'


def _queen_size(progress):
    if progress >= 75:
        return 'large'
    elif progress >= 50:
        return 'medium'
    elif progress >= 25:
        return 'small'
    return 'tiny'
