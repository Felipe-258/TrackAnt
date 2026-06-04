from django.shortcuts import render

def split_list(request):
    return render(request, 'splits/split_list.html')

def split_group_add(request):
    return render(request, 'splits/split_group_form.html')

def split_expense_add(request, group_id):
    return render(request, 'splits/split_expense_form.html')
