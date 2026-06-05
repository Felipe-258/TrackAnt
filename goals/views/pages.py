from decimal import Decimal, InvalidOperation

from django.db.models import F
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import Goal
from ..forms import GoalForm


def goal_list(request):
    goals = Goal.objects.select_related('currency').all()
    return render(request, 'goals/goal_list.html', {'goals': goals})


def goal_add(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            g = form.save()
            messages.success(request, f'🎯 Meta creada: {g.name}')
            return redirect('goals:goal_list')
    else:
        form = GoalForm()
    return render(request, 'goals/goal_form.html', {'form': form})


def goal_edit(request, pk):
    g = get_object_or_404(Goal, pk=pk)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=g)
        if form.is_valid():
            form.save()
            messages.success(request, f'Meta actualizada: {g.name}')
            return redirect('goals:goal_list')
    else:
        form = GoalForm(instance=g)
    return render(request, 'goals/goal_form.html', {'form': form, 'goal': g})


def goal_delete(request, pk):
    g = get_object_or_404(Goal, pk=pk)
    if request.method == 'POST':
        g.delete()
        messages.success(request, '🗑️ Meta eliminada')
        return redirect('goals:goal_list')
    return render(request, 'goals/goal_confirm_delete.html', {'goal': g})


def goal_add_progress(request, pk):
    g = get_object_or_404(Goal.objects.select_related('currency'), pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount)
            if amount > 0:
                if Goal.objects.filter(pk=pk).filter(current_amount__gte=F('target_amount') - amount).exists():
                    Goal.objects.filter(pk=pk).update(
                        current_amount=F('current_amount') + amount,
                        is_achieved=True,
                    )
                else:
                    Goal.objects.filter(pk=pk).update(
                        current_amount=F('current_amount') + amount,
                    )
                messages.success(request, f'💰 ${amount} agregado a "{g.name}"')
            else:
                messages.error(request, 'El monto debe ser mayor a cero')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Monto inválido')
        return redirect('goals:goal_list')
    return render(request, 'goals/goal_add_progress.html', {'goal': g})
