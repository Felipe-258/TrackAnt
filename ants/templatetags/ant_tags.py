from django import template
from ants.utils import get_colony_state

register = template.Library()


@register.inclusion_tag('ants/colony.html')
def ant_colony():
    return get_colony_state()


@register.simple_tag
def weather_icon(weather):
    icons = {
        'despejado': '☀️', 'soleado': '☀️', 'nublado': '⛅',
        'lluvioso': '🌧️', 'tormenta': '🌩️',
    }
    return icons.get(weather, '☀️')


@register.simple_tag
def queen_label(size):
    labels = {'tiny': '🐛', 'small': '🪱', 'medium': '🐜', 'large': '👑'}
    return labels.get(size, '')


@register.filter
def mod(num, val):
    return num % val


@register.filter
def mul(num, val):
    try:
        return float(num) * float(val)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def range_to(end):
    try:
        return range(int(end))
    except (TypeError, ValueError):
        return range(0)


@register.simple_tag
def time_of_day_icon(tod):
    icons = {'amanecer': '☀️', 'dia': '☀️', 'atardecer': '☀️', 'noche': '🌙'}
    return icons.get(tod, '☀️')


@register.filter
def list_get(lst, index):
    try:
        return lst[int(index)]
    except (IndexError, TypeError, ValueError):
        return '#B89472'
