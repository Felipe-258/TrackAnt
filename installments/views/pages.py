from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from ..models import InstallmentPurchase, Installment
from ..forms import InstallmentPurchaseForm


def _colony_purchases(request):
    return InstallmentPurchase.objects.filter(colony=request.colony)


def installment_list(request):
    from django.db.models import Sum

    active = list(_colony_purchases(request).filter(is_completed=False).select_related('currency').prefetch_related('installments'))

    all_installments = Installment.objects.filter(purchase__colony=request.colony)
    paid_count = all_installments.filter(is_paid=True).count()
    pending_count = all_installments.filter(is_paid=False).count()

    pending_rows = all_installments.filter(is_paid=False).values('purchase__currency__code').annotate(total=Sum('amount'))
    pending_by_currency = {r['purchase__currency__code']: r['total'] for r in pending_rows}

    total_rows = _colony_purchases(request).values('currency__code').annotate(total=Sum('total_amount'))
    total_by_currency = {r['currency__code']: r['total'] for r in total_rows}

    today = timezone.now().date()
    for p in active:
        inst_list = list(p.installments.all())
        p.paid_installments = sum(1 for i in inst_list if i.is_paid)
        p.progress_percent = int(p.paid_installments / p.installments_count * 100) if p.installments_count else 0
        next_inst = next((i for i in inst_list if not i.is_paid), None)
        p.next_installment = next_inst
        p.due_this_month = bool(next_inst and next_inst.due_date.year == today.year and next_inst.due_date.month == today.month)
        p.is_overdue = bool(next_inst and next_inst.due_date < today)

    summary = {
        'active_count': len(active),
        'paid_count': paid_count,
        'pending_count': pending_count,
        'pending_by_currency': pending_by_currency,
        'total_by_currency': total_by_currency,
    }

    completed = _colony_purchases(request).filter(is_completed=True).select_related('currency')[:20]
    return render(request, 'installments/installment_list.html', {
        'active_purchases': active,
        'completed_purchases': completed,
        'summary': summary,
    })


def installment_add(request):
    if request.method == 'POST':
        form = InstallmentPurchaseForm(request.POST, colony=request.colony)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.colony = request.colony
            purchase.save()
            _create_installments(purchase)
            messages.success(request, 'Compra en cuotas creada correctamente')
            return redirect('installments:list')
    else:
        form = InstallmentPurchaseForm(colony=request.colony)
    return render(request, 'installments/installment_form.html', {'form': form})


def installment_edit(request, pk):
    purchase = get_object_or_404(_colony_purchases(request), pk=pk)
    if request.method == 'POST':
        form = InstallmentPurchaseForm(request.POST, instance=purchase, colony=request.colony)
        if form.is_valid():
            purchase = form.save()
            purchase.installments.all().delete()
            _create_installments(purchase)
            messages.success(request, 'Compra actualizada correctamente')
            return redirect('installments:list')
    else:
        form = InstallmentPurchaseForm(instance=purchase, colony=request.colony)
    return render(request, 'installments/installment_form.html', {'form': form, 'purchase': purchase})


def installment_detail(request, pk):
    purchase = get_object_or_404(_colony_purchases(request).select_related('currency', 'category'), pk=pk)
    installments = list(purchase.installments.all().select_related('transaction'))
    from finances.exchange import available_balances
    balances = available_balances(request.colony)
    next_unpaid = next((i for i in installments if not i.is_paid), None)
    return render(request, 'installments/installment_detail.html', {
        'purchase': purchase,
        'installments': installments,
        'currency_available': balances.get(purchase.currency.code, 0),
        'next_unpaid': next_unpaid,
    })


def installment_pay(request, pk):
    installment = get_object_or_404(Installment.objects.filter(purchase__colony=request.colony), pk=pk)
    if installment.is_paid:
        messages.warning(request, 'Esta cuota ya está pagada')
    else:
        if request.colony.require_funds_for_conversion:
            from finances.exchange import available_balances
            avail = available_balances(request.colony).get(installment.purchase.currency.code, 0)
            if installment.amount > avail:
                messages.error(request, f'No tenés suficientes {installment.purchase.currency.code} (disponible: {avail:,.2f}). Convertí tu dinero en la página de Conversión.')
                return redirect('installments:detail', pk=installment.purchase_id)
        from trackant.utils import get_expense_category
        from finances.models import Transaction
        tx = Transaction.objects.create(
            colony=request.colony,
            type='EXPENSE',
            amount=installment.amount,
            currency=installment.purchase.currency,
            category=get_expense_category(request.colony.id, installment.purchase.category),
            date=timezone.now().date(),
            note=f'Cuota {installment.number}/{installment.purchase.installments_count} - {installment.purchase.name}',
            is_recurring=True,
        )
        installment.is_paid = True
        installment.paid_date = timezone.now().date()
        installment.transaction = tx
        installment.save()

        _check_completed(installment.purchase)

        messages.success(request, f'Cuota {installment.number} pagada correctamente')
    return redirect('installments:detail', pk=installment.purchase_id)


def installment_unpay(request, pk):
    installment = get_object_or_404(Installment.objects.filter(purchase__colony=request.colony), pk=pk)
    if not installment.is_paid:
        messages.warning(request, 'Esta cuota no está pagada')
    else:
        if installment.transaction:
            installment.transaction.delete()
            installment.transaction = None
        installment.is_paid = False
        installment.paid_date = None
        installment.save()

        purchase = installment.purchase
        purchase.is_completed = False
        purchase.save(update_fields=['is_completed'])

        messages.success(request, f'Pago de cuota {installment.number} revertido')
    return redirect('installments:detail', pk=installment.purchase_id)


def installment_delete(request, pk):
    purchase = get_object_or_404(_colony_purchases(request), pk=pk)
    if request.method == 'POST':
        purchase.installments.all().delete()
        purchase.delete()
        messages.success(request, 'Compra en cuotas eliminada')
        return redirect('installments:list')
    return render(request, 'installments/installment_confirm_delete.html', {'purchase': purchase})


def _create_installments(purchase):
    from decimal import Decimal
    from dateutil.relativedelta import relativedelta

    purchase.installments.all().delete()

    inst_amount = purchase.installment_amount or (purchase.total_amount / purchase.installments_count).quantize(Decimal('0.01'))
    for i in range(1, purchase.installments_count + 1):
        if i == purchase.installments_count:
            remaining = (purchase.total_amount - inst_amount * (i - 1)).quantize(Decimal('0.01'))
            amount = remaining if remaining > 0 else inst_amount
        else:
            amount = inst_amount

        due = purchase.start_date + relativedelta(months=i - 1)
        Installment.objects.create(
            purchase=purchase,
            number=i,
            due_date=due,
            amount=amount,
        )


def _check_completed(purchase):
    remaining = purchase.installments.filter(is_paid=False).count()
    if remaining == 0:
        purchase.is_completed = True
        purchase.save(update_fields=['is_completed'])
