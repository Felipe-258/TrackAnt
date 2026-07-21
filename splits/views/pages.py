from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from ..models import SplitGroup, SplitExpense
from ..forms import SplitGroupForm, SplitExpenseForm
from finances.models import Transaction, Category


def split_list(request):
    groups = SplitGroup.objects.filter(colony=request.colony)
    return render(request, 'splits/split_list.html', {'groups': groups})


def split_group_add(request):
    colony = request.colony
    if request.method == 'POST':
        form = SplitGroupForm(request.POST)
        if form.is_valid():
            g = form.save(commit=False)
            g.colony = colony
            g.save()
            messages.success(request, f'Grupo creado: {g.name}')
            return redirect('splits:split_list')
    else:
        form = SplitGroupForm()
    return render(request, 'splits/split_group_form.html', {'form': form})


def split_group_edit(request, pk):
    colony = request.colony
    group = get_object_or_404(SplitGroup, pk=pk, colony=colony)
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
    group = get_object_or_404(SplitGroup, pk=pk, colony=request.colony)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Grupo eliminado')
        return redirect('splits:split_list')
    return render(request, 'splits/split_group_confirm_delete.html', {'group': group})


def split_group_detail(request, pk):
    colony = request.colony
    group = get_object_or_404(SplitGroup.objects.filter(colony=colony).prefetch_related('expenses'), pk=pk)
    balance = group.balance()
    return render(request, 'splits/split_group_detail.html', {
        'group': group,
        'balance': balance,
    })


def split_expense_add(request, group_id):
    colony = request.colony
    group = get_object_or_404(SplitGroup, pk=group_id, colony=colony)
    if request.method == 'POST':
        form = SplitExpenseForm(request.POST, group=group, colony=colony)
        if form.is_valid():
            e = form.save(commit=False)
            e.group = group
            e.colony = colony
            num_members = len(group.members)
            share_amount = float(e.amount) / num_members if num_members > 0 else 0
            e.shares = {m: share_amount for m in group.members}
            e.save()
            if colony.auto_create_split_transactions:
                category, _ = Category.objects.get_or_create(
                    colony=colony,
                    name='Gasto compartido',
                    type='EXPENSE',
                    defaults={'icon': 'users', 'color': '#D4764A'},
                )
                Transaction.objects.create(
                    colony=colony,
                    type='EXPENSE',
                    amount=e.amount,
                    currency=e.currency,
                    category=category,
                    date=e.date,
                    note=f'Gasto compartido: {e.description}',
                )
            messages.success(request, f'Gasto agregado: {e.description}')
            return redirect('splits:split_group_detail', pk=group_id)
    else:
        form = SplitExpenseForm(initial={'date': date.today()}, group=group, colony=colony)
    return render(request, 'splits/split_expense_form.html', {'form': form, 'group': group})


def split_expense_edit(request, pk):
    colony = request.colony
    expense = get_object_or_404(SplitExpense, pk=pk, colony=colony)
    group = expense.group
    if request.method == 'POST':
        form = SplitExpenseForm(request.POST, instance=expense, group=group, colony=colony)
        if form.is_valid():
            e = form.save(commit=False)
            num_members = len(group.members)
            share_amount = float(e.amount) / num_members if num_members > 0 else 0
            e.shares = {m: share_amount for m in group.members}
            e.save()
            messages.success(request, f'Gasto actualizado: {e.description}')
            return redirect('splits:split_group_detail', pk=group.pk)
    else:
        form = SplitExpenseForm(instance=expense, group=group, colony=colony)
    return render(request, 'splits/split_expense_form.html', {'form': form, 'group': group, 'expense': expense})


def split_expense_delete(request, pk):
    colony = request.colony
    expense = get_object_or_404(SplitExpense, pk=pk, colony=colony)
    group_pk = expense.group.pk
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Gasto eliminado')
        return redirect('splits:split_group_detail', pk=group_pk)
    return render(request, 'splits/split_expense_confirm_delete.html', {'expense': expense})
