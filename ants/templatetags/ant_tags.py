from django import template
from ants.utils import get_financial_weather, get_queen_size

register = template.Library()


@register.inclusion_tag('ants/colony.html', takes_context=True)
def ant_colony(context):
    request = context.get('request')
    state = get_financial_weather(0, 0)
    queen = get_queen_size(0)
    return {
        'weather': state,
        'queen_size': queen,
        'worker_count': 0,
        'balance': 0,
    }


@register.simple_tag
def weather_emoji(weather):
    return {'sunny': '☀️', 'cloudy': '⛅', 'rainy': '🌧️', 'stormy': '🌩️'}.get(weather, '☀️')


@register.simple_tag
def queen_emoji(size):
    return {'tiny': '🐛', 'small': '🪱', 'medium': '🐜', 'large': '👑'}.get(size, '🐛')
