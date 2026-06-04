from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from ..models import Budget
from ..forms import BudgetForm


def budget_list(request):
    now = timezone.now()
    month = request.GET.get('month', now.month)
    year = request.GET.get('year', now.year)
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = now.month
        year = now.year

    budgets = Budget.objects.filter(month=month, year=year).select_related('category', 'currency')
    return render(request, 'budgets/budget_list.html', {
        'budgets': budgets,
        'month': month,
        'year': year,
    })


def budget_add(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            b = form.save()
            messages.success(request, f'📊 Presupuesto creado: {b.category.name}')
            return redirect('budgets:budget_list')
    else:
        now = timezone.now()
        form = BudgetForm(initial={'month': now.month, 'year': now.year})
    return render(request, 'budgets/budget_form.html', {'form': form})


def budget_edit(request, pk):
    b = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=b)
        if form.is_valid():
            form.save()
            messages.success(request, 'Presupuesto actualizado')
            return redirect('budgets:budget_list')
    else:
        form = BudgetForm(instance=b)
    return render(request, 'budgets/budget_form.html', {'form': form, 'budget': b})


def budget_delete(request, pk):
    b = get_object_or_404(Budget, pk=pk)
    if request.method == 'POST':
        b.delete()
        messages.success(request, '🗑️ Presupuesto eliminado')
        return redirect('budgets:budget_list')
    return render(request, 'budgets/budget_confirm_delete.html', {'budget': b})
