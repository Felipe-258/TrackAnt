from django.shortcuts import render

def debt_list(request):
    return render(request, 'debts/debt_list.html')

def debt_add(request):
    return render(request, 'debts/debt_form.html')

def debt_edit(request, pk):
    return render(request, 'debts/debt_form.html')

def debt_delete(request, pk):
    return render(request, 'debts/debt_confirm_delete.html')
