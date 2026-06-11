from django.shortcuts import render
from ants.utils import get_colony_state
from goals.models import Goal


def colony_view(request):
    colony = request.colony
    goal_id = request.GET.get('goal_id')
    try:
        goal_id = int(goal_id) if goal_id else None
    except (ValueError, TypeError):
        goal_id = None

    state = get_colony_state(colony=colony, goal_id=goal_id)
    state['active_goals_list'] = Goal.objects.filter(colony=colony, is_achieved=False).only('id', 'name')
    state['selected_goal_id'] = goal_id

    return render(request, 'ants/colony_page.html', state)


def playground(request):
    state = get_colony_state(colony=request.colony)
    return render(request, 'ants/playground.html', state)
