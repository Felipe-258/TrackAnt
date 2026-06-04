from datetime import datetime

def get_colony_state(user=None):
    total_balance = 0
    monthly_income = 0
    monthly_expenses = 0
    active_goals = 0
    active_goals_progress = 0

    if user:
        pass

    worker_ants = min(abs(monthly_income) + abs(monthly_expenses) // 1000, 50)
    weather = get_financial_weather(monthly_income, monthly_expenses)
    queen_size = get_queen_size(active_goals_progress)

    return {
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'active_goals': active_goals,
        'worker_ants': worker_ants or 0,
        'weather': weather,
        'queen_size': queen_size,
        'queen_progress': active_goals_progress,
    }


def get_financial_weather(income, expenses):
    if income > expenses * 1.5:
        return 'sunny'
    elif income >= expenses:
        return 'cloudy'
    elif income >= expenses * 0.75:
        return 'rainy'
    else:
        return 'stormy'


def get_queen_size(progress):
    if progress >= 75:
        return 'large'
    elif progress >= 50:
        return 'medium'
    elif progress >= 25:
        return 'small'
    return 'tiny'
