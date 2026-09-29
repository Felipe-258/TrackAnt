from decimal import Decimal, InvalidOperation

from django.db.models import F
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from ..models import Reserve
from ..forms import ReserveForm


def reserve_list(request):
    reserves = Reserve.objects.filter(colony=request.colony).select_related('currency')
    return render(request, 'reserves/reserve_list.html', {'reserves': reserves})


def reserve_add(request):
    colony = request.colony
    if request.method == 'POST':
        form = ReserveForm(request.POST, colony=colony)
        if form.is_valid():
            r = form.save(commit=False)
            r.colony = colony
            r.save()
            messages.success(request, f'Reserva creada: {r.name}')
            return redirect('reserves:list')
    else:
        form = ReserveForm(colony=colony)
    return render(request, 'reserves/reserve_form.html', {'form': form})


def reserve_edit(request, pk):
    colony = request.colony
    r = get_object_or_404(Reserve, pk=pk, colony=colony)
    if request.method == 'POST':
        form = ReserveForm(request.POST, instance=r, colony=colony)
        if form.is_valid():
            form.save()
            messages.success(request, f'Reserva actualizada: {r.name}')
            return redirect('reserves:list')
    else:
        form = ReserveForm(instance=r, colony=colony)
    return render(request, 'reserves/reserve_form.html', {'form': form, 'reserve': r})


def reserve_delete(request, pk):
    r = get_object_or_404(Reserve, pk=pk, colony=request.colony)
    if request.method == 'POST':
        r.delete()
        messages.success(request, 'Reserva eliminada')
        return redirect('reserves:list')
    return render(request, 'reserves/reserve_confirm_delete.html', {'reserve': r})


def reserve_deposit(request, pk):
    colony = request.colony
    r = get_object_or_404(Reserve.objects.filter(colony=colony).select_related('currency'), pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount)
            if amount > 0:
                if r.has_target:
                    if Reserve.objects.filter(pk=pk, colony=colony).filter(current_amount__gte=F('target_amount') - amount).exists():
                        Reserve.objects.filter(pk=pk, colony=colony).update(
                            current_amount=F('current_amount') + amount,
                            is_achieved=True,
                        )
                    else:
                        Reserve.objects.filter(pk=pk, colony=colony).update(
                            current_amount=F('current_amount') + amount,
                        )
                else:
                    Reserve.objects.filter(pk=pk, colony=colony).update(
                        current_amount=F('current_amount') + amount,
                    )
                messages.success(request, f'${amount} apartado en "{r.name}"')
            else:
                messages.error(request, 'El monto debe ser mayor a cero')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Monto invalido')
        return redirect('reserves:list')
    return render(request, 'reserves/reserve_deposit.html', {'reserve': r})


def reserve_withdraw(request, pk):
    colony = request.colony
    r = get_object_or_404(Reserve.objects.filter(colony=colony).select_related('currency'), pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
            else:
                updated = Reserve.objects.filter(
                    pk=pk, colony=colony, current_amount__gte=amount
                ).update(
                    current_amount=F('current_amount') - amount,
                    is_achieved=False,
                )
                if updated:
                    messages.success(request, f'${amount} retirado de "{r.name}"')
                else:
                    messages.error(request, 'No hay suficiente saldo en la reserva')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Monto invalido')
        return redirect('reserves:list')
    return render(request, 'reserves/reserve_withdraw.html', {'reserve': r})
