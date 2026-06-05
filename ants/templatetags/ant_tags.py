from django import template
from django.utils.safestring import mark_safe
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


@register.simple_tag
def render_leaf_pile(brown, green, spread_x, spread_y):
    brown = int(brown) if brown else 0
    green = int(green) if green else 0
    rows = [
        (7, (-24,-16,-8,0,8,16,24),  0, (-12,-8,-4,0,4,8,12)),
        (5, (-16,-8,0,8,16),          -6, (-8,-4,0,4,8)),
        (4, (-12,-4,4,12),            -11, (-6,-2,2,6)),
        (3, (-8,0,8),                  -16, (-4,0,4)),
        (2, (-4,4),                   -21, (-2,2)),
        (1, (0,),                      -26, (0,)),
    ]
    html = ''
    c = brown
    for n, xs, y, rots in rows:
        taken = min(n, c)
        for j in range(taken):
            html += f'<text x="{xs[j]}" y="{y}" font-size="14" opacity="0.80" transform="rotate({rots[j]}, {xs[j]}, {y})">🍂</text>'
        c -= taken
        if c <= 0:
            break
    c = green
    rows_g = [
        (5, (-20,-10,0,10,20),         -2, (-8,-4,0,4,8)),
        (3, (-10,0,10),                -8, (-4,0,4)),
        (2, (-6,6),                    -13, (-3,3)),
    ]
    for n, xs, y, rots in rows_g:
        taken = min(n, c)
        for j in range(taken):
            html += f'<text x="{xs[j]}" y="{y}" font-size="12" opacity="0.60" transform="rotate({rots[j]}, {xs[j]}, {y})">🍃</text>'
        c -= taken
        if c <= 0:
            break
    return mark_safe(html)


@register.filter
def list_get(lst, index):
    try:
        return lst[int(index)]
    except (IndexError, TypeError, ValueError):
        return '#B89472'
