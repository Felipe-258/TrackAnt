from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from ..models import SplitGroup, SplitExpense, SplitPayment
from ..forms import SplitGroupForm, SplitExpenseForm
from finances.models import Transaction, Category, Currency


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
    group = get_object_or_404(
        SplitGroup.objects.filter(colony=colony).prefetch_related('expenses', 'payments'),
        pk=pk,
    )
    balances = group.balance_by_currency()
    debts = group.settle_debts()
    prefs = group.payment_preferences or {}
    symbol_map = {}
    for e in group.expenses.select_related('currency').all():
        symbol_map.setdefault(e.currency.code, e.currency.symbol)
    for p in group.payments.select_related('currency').all():
        symbol_map.setdefault(p.currency.code, p.currency.symbol)
    for d in debts:
        d['preferred'] = prefs.get(d['payer']) == d['payee']
        d['currency_symbol'] = symbol_map.get(d['currency_code'], d['currency_code'])
    return render(request, 'splits/split_group_detail.html', {
        'group': group,
        'balances': balances,
        'debts': debts,
        'payments': group.payments.select_related('currency').order_by('-date'),
        'symbols': symbol_map,
        'preferences': prefs,
    })


def split_payment_add(request, pk):
    colony = request.colony
    group = get_object_or_404(SplitGroup, pk=pk, colony=colony)
    if request.method == 'POST':
        payer = request.POST.get('payer', '').strip()
        payee = request.POST.get('payee', '').strip()
        amount = request.POST.get('amount', '')
        currency_id = request.POST.get('currency', '')
        try:
            amount = Decimal(amount)
        except (InvalidOperation, ValueError):
            messages.error(request, 'Monto invalido')
            return redirect('splits:split_group_detail', pk=pk)
        if payer not in group.members or payee not in group.members:
            messages.error(request, 'Pagador y receptor deben ser miembros del grupo')
            return redirect('splits:split_group_detail', pk=pk)
        if payer == payee:
            messages.error(request, 'El pagador y el receptor no pueden ser la misma persona')
            return redirect('splits:split_group_detail', pk=pk)
        if amount <= 0:
            messages.error(request, 'El monto debe ser mayor a cero')
            return redirect('splits:split_group_detail', pk=pk)
        currency = Currency.objects.filter(code=currency_id).first()
        if currency is None:
            messages.error(request, 'Moneda invalida')
            return redirect('splits:split_group_detail', pk=pk)
        SplitPayment.objects.create(
            group=group, payer=payer, payee=payee,
            amount=amount, currency=currency, date=date.today(),
        )
        messages.success(request, f'Pago registrado: {payer} pagó {currency.symbol}{amount} a {payee}')
    return redirect('splits:split_group_detail', pk=pk)


def split_payment_delete(request, pk):
    colony = request.colony
    payment = get_object_or_404(SplitPayment, pk=pk, group__colony=colony)
    group_pk = payment.group.pk
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Pago eliminado')
    return redirect('splits:split_group_detail', pk=group_pk)


def split_preference_add(request, pk):
    colony = request.colony
    group = get_object_or_404(SplitGroup, pk=pk, colony=colony)
    if request.method == 'POST':
        payer = request.POST.get('payer', '').strip()
        payee = request.POST.get('payee', '').strip()
        if payer not in group.members or payee not in group.members:
            messages.error(request, 'Ambos deben ser miembros del grupo')
            return redirect('splits:split_group_detail', pk=pk)
        if payer == payee:
            messages.error(request, 'El pagador y el receptor no pueden ser la misma persona')
            return redirect('splits:split_group_detail', pk=pk)
        prefs = dict(group.payment_preferences or {})
        prefs[payer] = payee
        group.payment_preferences = prefs
        group.save(update_fields=['payment_preferences'])
        messages.success(request, f'Preferencia guardada: {payer} prefiere pagarle a {payee}')
    return redirect('splits:split_group_detail', pk=pk)


def split_preference_remove(request, pk):
    colony = request.colony
    group = get_object_or_404(SplitGroup, pk=pk, colony=colony)
    if request.method == 'POST':
        payer = request.POST.get('payer', '').strip()
        prefs = dict(group.payment_preferences or {})
        if payer in prefs:
            del prefs[payer]
            group.payment_preferences = prefs
            group.save(update_fields=['payment_preferences'])
            messages.success(request, 'Preferencia eliminada')
    return redirect('splits:split_group_detail', pk=pk)


def split_expense_add(request, group_id):
    colony = request.colony
    group = get_object_or_404(SplitGroup, pk=group_id, colony=colony)
    if request.method == 'POST':
        form = SplitExpenseForm(request.POST, group=group, colony=colony)
        if form.is_valid():
            e = form.save(commit=False)
            e.group = group
            num_members = len(group.members)
            if num_members > 0:
                share = (Decimal(e.amount) / num_members).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                e.shares = {m: float(share) for m in group.members}
            else:
                e.shares = {}
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
    expense = get_object_or_404(SplitExpense, pk=pk, group__colony=colony)
    group = expense.group
    if request.method == 'POST':
        form = SplitExpenseForm(request.POST, instance=expense, group=group, colony=colony)
        if form.is_valid():
            e = form.save(commit=False)
            num_members = len(group.members)
            if num_members > 0:
                share = (Decimal(e.amount) / num_members).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                e.shares = {m: float(share) for m in group.members}
            else:
                e.shares = {}
            e.save()
            messages.success(request, f'Gasto actualizado: {e.description}')
            return redirect('splits:split_group_detail', pk=group.pk)
    else:
        form = SplitExpenseForm(instance=expense, group=group, colony=colony)
    return render(request, 'splits/split_expense_form.html', {'form': form, 'group': group, 'expense': expense})


def split_expense_delete(request, pk):
    colony = request.colony
    expense = get_object_or_404(SplitExpense, pk=pk, group__colony=colony)
    group_pk = expense.group.pk
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Gasto eliminado')
        return redirect('splits:split_group_detail', pk=group_pk)
    return render(request, 'splits/split_expense_confirm_delete.html', {'expense': expense})
