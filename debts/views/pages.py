from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from ..models import Debt, DebtPayment
from ..forms import DebtForm, DebtPaymentForm
from finances.models import Transaction, Category


def debt_list(request):
    colony = request.colony
    debts_all = Debt.objects.filter(colony=colony, is_settled=False).select_related('currency')
    debts_owe = debts_all.filter(debt_type='OWE')
    debts_owed = debts_all.filter(debt_type='OWED')
    settled = Debt.objects.filter(colony=colony, is_settled=True).select_related('currency')[:10]
    return render(request, 'debts/debt_list.html', {
        'debts_all': debts_all,
        'debts_owe': debts_owe,
        'debts_owed': debts_owed,
        'settled': settled,
    })


def debt_add(request):
    colony = request.colony
    if request.method == 'POST':
        form = DebtForm(request.POST, colony=colony)
        if form.is_valid():
            d = form.save(commit=False)
            d.colony = colony
            d.save()
            messages.success(request, f'Deuda registrada con {d.person}')
            return redirect('debts:debt_list')
    else:
        form = DebtForm(initial={'date': date.today(), 'debt_type': request.GET.get('type', 'OWE')}, colony=colony)
    return render(request, 'debts/debt_form.html', {'form': form})


def debt_edit(request, pk):
    colony = request.colony
    d = get_object_or_404(Debt, pk=pk, colony=colony)
    if request.method == 'POST':
        form = DebtForm(request.POST, instance=d, colony=colony)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deuda actualizada')
            return redirect('debts:debt_list')
    else:
        form = DebtForm(instance=d, colony=colony)
    return render(request, 'debts/debt_form.html', {'form': form, 'debt': d})


def debt_delete(request, pk):
    d = get_object_or_404(Debt, pk=pk, colony=request.colony)
    if request.method == 'POST':
        d.delete()
        messages.success(request, 'Deuda eliminada')
        return redirect('debts:debt_list')
    return render(request, 'debts/debt_confirm_delete.html', {'debt': d})


def debt_detail(request, pk):
    colony = request.colony
    d = get_object_or_404(Debt.objects.filter(colony=colony).select_related('currency'), pk=pk)
    payments = d.payments.all()
    if request.method == 'POST':
        form = DebtPaymentForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.debt = d
            p.save()
            if d.remaining() <= 0:
                d.is_settled = True
                d.save()
            if colony.auto_create_debt_transactions:
                category, _ = Category.objects.get_or_create(
                    colony=colony,
                    name='Pago de deuda',
                    type='EXPENSE',
                    defaults={'icon': 'credit-card', 'color': '#D4764A'},
                )
                Transaction.objects.create(
                    colony=colony,
                    type='EXPENSE',
                    amount=p.amount,
                    currency=d.currency,
                    category=category,
                    date=p.date,
                    note=f'Pago de deuda a {d.person}',
                )
            messages.success(request, f'Pago de ${p.amount} registrado')
            return redirect('debts:debt_detail', pk=pk)
    else:
        form = DebtPaymentForm(initial={'date': date.today()})
    return render(request, 'debts/debt_detail.html', {
        'debt': d,
        'payments': payments,
        'form': form,
    })
