from django.shortcuts import render

def dashboard(request):
    return render(request, 'finances/dashboard.html')

def transaction_list(request):
    return render(request, 'finances/transaction_list.html')

def transaction_add(request):
    return render(request, 'finances/transaction_form.html')

def transaction_edit(request, pk):
    return render(request, 'finances/transaction_form.html')

def transaction_delete(request, pk):
    return render(request, 'finances/transaction_confirm_delete.html')

def income_list(request):
    return render(request, 'finances/income_list.html')

def expense_list(request):
    return render(request, 'finances/expense_list.html')

def category_list(request):
    return render(request, 'finances/category_list.html')
