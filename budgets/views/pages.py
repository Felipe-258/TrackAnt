from django.shortcuts import render

def budget_list(request):
    return render(request, 'budgets/budget_list.html')

def budget_add(request):
    return render(request, 'budgets/budget_form.html')

def budget_edit(request, pk):
    return render(request, 'budgets/budget_form.html')

def budget_delete(request, pk):
    return render(request, 'budgets/budget_confirm_delete.html')
