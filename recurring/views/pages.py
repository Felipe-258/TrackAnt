from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import RecurringTransaction
from ..forms import RecurringTransactionForm


def _colony_transactions(request):
    return RecurringTransaction.objects.filter(colony=request.colony)


def recurring_list(request):
    active = _colony_transactions(request).filter(is_active=True).select_related('currency', 'category')
    inactive = _colony_transactions(request).filter(is_active=False).select_related('currency')[:20]
    return render(request, 'recurring/recurring_list.html', {
        'active': active,
        'inactive': inactive,
    })


def recurring_add(request):
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, colony=request.colony)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.colony = request.colony
            if not obj.next_date:
                obj.next_date = obj.start_date
            obj.save()
            messages.success(request, 'Gasto recurrente creado correctamente')
            return redirect('recurring:list')
    else:
        form = RecurringTransactionForm(colony=request.colony)
    return render(request, 'recurring/recurring_form.html', {'form': form})


def recurring_edit(request, pk):
    obj = get_object_or_404(_colony_transactions(request), pk=pk)
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, instance=obj, colony=request.colony)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto recurrente actualizado')
            return redirect('recurring:list')
    else:
        form = RecurringTransactionForm(instance=obj, colony=request.colony)
    return render(request, 'recurring/recurring_form.html', {'form': form})


def recurring_delete(request, pk):
    obj = get_object_or_404(_colony_transactions(request), pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Gasto recurrente eliminado')
        return redirect('recurring:list')
    return render(request, 'recurring/recurring_confirm_delete.html', {'object': obj})
