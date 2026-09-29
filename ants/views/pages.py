from django.shortcuts import render
from ants.utils import get_colony_state
from goals.models import Reserve


def colony_view(request):
    colony = request.colony
    reserve_id = request.GET.get('reserve_id')
    try:
        reserve_id = int(reserve_id) if reserve_id else None
    except (ValueError, TypeError):
        reserve_id = None

    state = get_colony_state(colony=colony, reserve_id=reserve_id)
    state['active_reserves_list'] = Reserve.objects.filter(colony=colony, is_achieved=False).only('id', 'name')
    state['selected_reserve_id'] = reserve_id

    return render(request, 'ants/colony_page.html', state)


def playground(request):
    state = get_colony_state(colony=request.colony)
    return render(request, 'ants/playground.html', state)
