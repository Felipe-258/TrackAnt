from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from ..models import Subscription, SubscriptionPayment
from ..forms import SubscriptionForm
from ..services import mark_as_paid, mark_as_unpaid


def subscription_list(request):
    colony = request.colony
    today = timezone.now().date()

    active = Subscription.objects.filter(colony=colony, is_active=True).select_related('currency', 'category')
    inactive = Subscription.objects.filter(colony=colony, is_active=False).select_related('currency')
    total_monthly = sum(s.monthly_cost() for s in active)

    pending_payments = SubscriptionPayment.objects.filter(
        subscription__colony=colony,
        subscription__is_active=True,
        is_paid=False,
        due_date__lte=today + timedelta(days=7),
    ).select_related('subscription__currency', 'subscription__category').order_by('due_date')

    recent_paid = SubscriptionPayment.objects.filter(
        subscription__colony=colony,
        subscription__is_active=True,
        is_paid=True,
    ).select_related('subscription__currency', 'subscription__category').order_by('-paid_date')[:10]

    for payment in pending_payments:
        delta = (payment.due_date - today).days
        if delta < 0:
            payment.status = 'overdue'
            payment.status_label = f'Vencida hace {abs(delta)} dias'
        elif delta == 0:
            payment.status = 'today'
            payment.status_label = 'Vence hoy'
        elif delta <= 3:
            payment.status = 'soon'
            payment.status_label = f'En {delta} dias'
        else:
            payment.status = 'upcoming'
            payment.status_label = payment.due_date.strftime('%d/%m/%Y')

    return render(request, 'subscriptions/subscription_list.html', {
        'active': active,
        'inactive': inactive,
        'total_monthly': total_monthly,
        'pending_payments': pending_payments,
        'recent_paid': recent_paid,
    })


def subscription_add(request):
    colony = request.colony
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, colony=colony)
        if form.is_valid():
            s = form.save(commit=False)
            s.colony = colony
            s.save()
            messages.success(request, f'Suscripcion agregada: {s.name}')
            return redirect('subscriptions:subscription_list')
    else:
        form = SubscriptionForm(colony=colony)
    return render(request, 'subscriptions/subscription_form.html', {'form': form})


def subscription_edit(request, pk):
    colony = request.colony
    s = get_object_or_404(Subscription, pk=pk, colony=colony)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=s, colony=colony)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suscripcion actualizada')
            return redirect('subscriptions:subscription_list')
    else:
        form = SubscriptionForm(instance=s, colony=colony)
    return render(request, 'subscriptions/subscription_form.html', {'form': form, 'subscription': s})


def subscription_delete(request, pk):
    s = get_object_or_404(Subscription, pk=pk, colony=request.colony)
    if request.method == 'POST':
        s.delete()
        messages.success(request, 'Suscripcion eliminada')
        return redirect('subscriptions:subscription_list')
    return render(request, 'subscriptions/subscription_confirm_delete.html', {'subscription': s})


def subscription_toggle_paid(request, pk):
    payment = get_object_or_404(
        SubscriptionPayment,
        pk=pk,
        subscription__colony=request.colony,
    )

    if request.method == 'POST':
        if payment.is_paid:
            mark_as_unpaid(payment)
            messages.warning(request, f'Pago de {payment.subscription.name} marcado como no pagado')
        else:
            mark_as_paid(payment)
            messages.success(request, f'{payment.subscription.name} marcada como pagada')

    return redirect('subscriptions:subscription_list')
