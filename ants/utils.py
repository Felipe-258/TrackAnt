from datetime import date
from django.db.models import Sum, Q
from finances.models import Transaction
from goals.models import Reserve
from budgets.models import Budget


def get_colony_state(colony, reserve_id=None):
    today = date.today()
    year, month = today.year, today.month

    month_qs = Transaction.objects.filter(colony=colony, date__year=year, date__month=month)
    monthly_income = float(month_qs.filter(type='INCOME').aggregate(s=Sum('amount'))['s'] or 0)
    monthly_expenses = float(month_qs.filter(type='EXPENSE').aggregate(s=Sum('amount'))['s'] or 0)

    total = Transaction.objects.filter(colony=colony).aggregate(
        i=Sum('amount', filter=Q(type='INCOME')),
        e=Sum('amount', filter=Q(type='EXPENSE')),
    )
    total_balance = float((total['i'] or 0) - (total['e'] or 0))

    reserved_total = float(Reserve.objects.filter(colony=colony).aggregate(s=Sum('current_amount'))['s'] or 0)
    total_balance = total_balance - reserved_total

    transaction_count = Transaction.objects.filter(colony=colony).count()
    active_reserves = Reserve.objects.filter(colony=colony, is_achieved=False).count()

    main_reserve = None
    if reserve_id:
        main_reserve = Reserve.objects.filter(id=reserve_id, colony=colony, is_achieved=False).first()
    if main_reserve is None:
        main_reserve = Reserve.objects.filter(colony=colony, is_achieved=False).first()

    goal_progress = main_reserve.progress_pct() if main_reserve and main_reserve.has_target else 0
    goal_color = main_reserve.color if main_reserve else '#C4943A'

    over_budget = Budget.objects.filter(
        colony=colony, month=month, year=year
    ).select_related('category').all()
    budget_alerts = sum(1 for b in over_budget if b.pct() >= 80)

    worker_ants = min(transaction_count, 12)
    soldier_ants = min(budget_alerts, 4)

    recent = list(Transaction.objects.filter(colony=colony).order_by('-date')[:worker_ants])
    leaf_colors = ['#6E8F4C' if t.type == 'INCOME' else '#D4764A' for t in recent]

    weather = _get_weather(monthly_income, monthly_expenses)
    queen_size = _queen_size(goal_progress)
    tod, tod_icon, sun_left, sun_top = get_time_of_day()

    # Ant speed based on weather
    speed_map = {'despejado': 16, 'soleado': 16, 'nublado': 16, 'lluvioso': 22, 'tormenta': 28}
    ant_speed = speed_map.get(weather, 16)

    # Leaf pile: proportional to reserve progress
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
        'active_reserves': active_reserves,
        'transaction_count': transaction_count,
        'goal_name': main_reserve.name if main_reserve else None,
        'goal_currency': str(main_reserve.currency.symbol) if main_reserve else '',
        'goal_current': float(main_reserve.current_amount) if main_reserve else 0,
        'goal_target': float(main_reserve.target_amount) if main_reserve and main_reserve.has_target else 0,
        'goal_color': goal_color,
        'leaf_colors': leaf_colors,
        'leaf_brown_count': leaf_brown,
        'leaf_green_count': leaf_green,
        'tod': tod,
        'tod_icon': tod_icon,
        'sun_left': int(sun_left),
        'sun_top': int(sun_top),
        'ant_speed': ant_speed,
    }


def _get_weather(income, expenses):
    if income == 0 and expenses == 0:
        return 'despejado'
    if income >= expenses * 1.5:
        return 'soleado'
    elif income >= expenses:
        return 'nublado'
    elif expenses == 0 and income > 0:
        return 'soleado'
    elif income >= expenses * 0.5:
        return 'lluvioso'
    else:
        return 'tormenta'


def get_time_of_day():
    from datetime import datetime
    from django.utils import timezone
    now = timezone.localtime()
    hour = now.hour

    # Sun position: interpolate between 5am (east, low) → 12pm (center, high) → 8pm (west, low)
    if 5 <= hour < 12:
        t = (hour - 5) / 7.0  # 0 → 1
        left = 8 + (42 * t)    # 8% → 50%
        top = 55 - (47 * t)    # 55% → 8%
    elif 12 <= hour < 20:
        t = (hour - 12) / 8.0  # 0 → 1
        left = 50 + (42 * t)    # 50% → 92%
        top = 8 + (47 * t)      # 8% → 55%
    else:
        left, top = -10, -10    # hidden (night, moon follows same logic)

    if 5 <= hour < 7:
        return 'amanecer', 'sun.svg', left, top
    elif 7 <= hour < 18:
        return 'dia', 'sun.svg', left, top
    elif 18 <= hour < 20:
        return 'atardecer', 'sun.svg', left, top
    else:
        # Moon follows same path as sun
        moon_left, moon_top = left, top
        if hour >= 20:
            t = (hour - 20) / 9.0  # 0 at 20h → 1 at 5h
            moon_left = 92 + (-84 * min(t, 1))
            moon_top = 55 - (47 * min(t, 1))
        elif hour < 5:
            t = (hour + 4) / 9.0
            moon_left = 8 + (42 * min(t, 1))
            moon_top = 55 - (47 * min(t, 1))
        return 'noche', 'moon.svg', moon_left, moon_top


def _queen_size(progress):
    if progress >= 75:
        return 'large'
    elif progress >= 50:
        return 'medium'
    elif progress >= 25:
        return 'small'
    return 'tiny'
