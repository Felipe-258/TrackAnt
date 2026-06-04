from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import Debt, DebtPayment
from ..forms import DebtForm, DebtPaymentForm


def debt_list(request):
    debts_owe = Debt.objects.filter(debt_type='OWE', is_settled=False).select_related('currency')
    debts_owed = Debt.objects.filter(debt_type='OWED', is_settled=False).select_related('currency')
    settled = Debt.objects.filter(is_settled=True).select_related('currency')[:10]
    return render(request, 'debts/debt_list.html', {
        'debts_owe': debts_owe,
        'debts_owed': debts_owed,
        'settled': settled,
    })


def debt_add(request):
    if request.method == 'POST':
        form = DebtForm(request.POST)
        if form.is_valid():
            d = form.save()
            messages.success(request, f'💳 Deuda registrada con {d.person}')
            return redirect('debts:debt_list')
    else:
        form = DebtForm(initial={'date': __import__('datetime').date.today(), 'debt_type': request.GET.get('type', 'OWE')})
    return render(request, 'debts/debt_form.html', {'form': form})


def debt_edit(request, pk):
    d = get_object_or_404(Debt, pk=pk)
    if request.method == 'POST':
        form = DebtForm(request.POST, instance=d)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deuda actualizada')
            return redirect('debts:debt_list')
    else:
        form = DebtForm(instance=d)
    return render(request, 'debts/debt_form.html', {'form': form, 'debt': d})


def debt_delete(request, pk):
    d = get_object_or_404(Debt, pk=pk)
    if request.method == 'POST':
        d.delete()
        messages.success(request, '🗑️ Deuda eliminada')
        return redirect('debts:debt_list')
    return render(request, 'debts/debt_confirm_delete.html', {'debt': d})


def debt_detail(request, pk):
    d = get_object_or_404(Debt.objects.select_related('currency'), pk=pk)
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
            messages.success(request, f'💰 Pago de ${p.amount} registrado')
            return redirect('debts:debt_detail', pk=pk)
    else:
        form = DebtPaymentForm(initial={'date': __import__('datetime').date.today()})
    return render(request, 'debts/debt_detail.html', {
        'debt': d,
        'payments': payments,
        'form': form,
    })
