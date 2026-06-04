from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from ..models import Subscription
from ..forms import SubscriptionForm


def subscription_list(request):
    active = Subscription.objects.filter(is_active=True).select_related('currency', 'category')
    inactive = Subscription.objects.filter(is_active=False).select_related('currency')
    total_monthly = sum(s.monthly_cost() for s in active)
    return render(request, 'subscriptions/subscription_list.html', {
        'active': active,
        'inactive': inactive,
        'total_monthly': total_monthly,
    })


def subscription_add(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            s = form.save()
            messages.success(request, f'🔄 Suscripción agregada: {s.name}')
            return redirect('subscriptions:subscription_list')
    else:
        form = SubscriptionForm()
    return render(request, 'subscriptions/subscription_form.html', {'form': form})


def subscription_edit(request, pk):
    s = get_object_or_404(Subscription, pk=pk)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=s)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suscripción actualizada')
            return redirect('subscriptions:subscription_list')
    else:
        form = SubscriptionForm(instance=s)
    return render(request, 'subscriptions/subscription_form.html', {'form': form, 'subscription': s})


def subscription_delete(request, pk):
    s = get_object_or_404(Subscription, pk=pk)
    if request.method == 'POST':
        s.delete()
        messages.success(request, '🗑️ Suscripción eliminada')
        return redirect('subscriptions:subscription_list')
    return render(request, 'subscriptions/subscription_confirm_delete.html', {'subscription': s})
