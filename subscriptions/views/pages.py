from django.shortcuts import render

def subscription_list(request):
    return render(request, 'subscriptions/subscription_list.html')

def subscription_add(request):
    return render(request, 'subscriptions/subscription_form.html')

def subscription_edit(request, pk):
    return render(request, 'subscriptions/subscription_form.html')

def subscription_delete(request, pk):
    return render(request, 'subscriptions/subscription_confirm_delete.html')
