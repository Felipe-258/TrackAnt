from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import SplitGroup, SplitExpense
from ..forms import SplitGroupForm, SplitExpenseForm


def split_list(request):
    groups = SplitGroup.objects.all()
    return render(request, 'splits/split_list.html', {'groups': groups})


def split_group_add(request):
    if request.method == 'POST':
        form = SplitGroupForm(request.POST)
        if form.is_valid():
            g = form.save()
            messages.success(request, f'👥 Grupo creado: {g.name}')
            return redirect('splits:split_list')
    else:
        form = SplitGroupForm()
    return render(request, 'splits/split_group_form.html', {'form': form})


def split_group_edit(request, pk):
    group = get_object_or_404(SplitGroup, pk=pk)
    if request.method == 'POST':
        form = SplitGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'Grupo actualizado: {group.name}')
            return redirect('splits:split_group_detail', pk=pk)
    else:
        form = SplitGroupForm(instance=group)
    return render(request, 'splits/split_group_form.html', {'form': form, 'group': group})


def split_group_delete(request, pk):
    group = get_object_or_404(SplitGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, '🗑️ Grupo eliminado')
        return redirect('splits:split_list')
    return render(request, 'splits/split_group_confirm_delete.html', {'group': group})


def split_group_detail(request, pk):
    group = get_object_or_404(SplitGroup.objects.prefetch_related('expenses'), pk=pk)
    balance = group.balance()
    return render(request, 'splits/split_group_detail.html', {
        'group': group,
        'balance': balance,
    })


def split_expense_add(request, group_id):
    group = get_object_or_404(SplitGroup, pk=group_id)
    if request.method == 'POST':
        form = SplitExpenseForm(request.POST, group=group)
        if form.is_valid():
            e = form.save(commit=False)
            e.group = group
            num_members = len(group.members)
            share_amount = float(e.amount) / num_members if num_members > 0 else 0
            e.shares = {m: share_amount for m in group.members}
            e.save()
            messages.success(request, f'💰 Gasto agregado: {e.description}')
            return redirect('splits:split_group_detail', pk=group_id)
    else:
        form = SplitExpenseForm(initial={'date': __import__('datetime').date.today()}, group=group)
    return render(request, 'splits/split_expense_form.html', {'form': form, 'group': group})


def split_expense_edit(request, pk):
    expense = get_object_or_404(SplitExpense, pk=pk)
    group = expense.group
    if request.method == 'POST':
        form = SplitExpenseForm(request.POST, instance=expense, group=group)
        if form.is_valid():
            e = form.save(commit=False)
            num_members = len(group.members)
            share_amount = float(e.amount) / num_members if num_members > 0 else 0
            e.shares = {m: share_amount for m in group.members}
            e.save()
            messages.success(request, f'Gasto actualizado: {e.description}')
            return redirect('splits:split_group_detail', pk=group.pk)
    else:
        form = SplitExpenseForm(instance=expense, group=group)
    return render(request, 'splits/split_expense_form.html', {'form': form, 'group': group, 'expense': expense})


def split_expense_delete(request, pk):
    expense = get_object_or_404(SplitExpense, pk=pk)
    group_pk = expense.group.pk
    if request.method == 'POST':
        expense.delete()
        messages.success(request, '🗑️ Gasto eliminado')
        return redirect('splits:split_group_detail', pk=group_pk)
    return render(request, 'splits/split_expense_confirm_delete.html', {'expense': expense})
