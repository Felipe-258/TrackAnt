from django.shortcuts import render

def goal_list(request):
    return render(request, 'goals/goal_list.html')

def goal_add(request):
    return render(request, 'goals/goal_form.html')

def goal_edit(request, pk):
    return render(request, 'goals/goal_form.html')

def goal_delete(request, pk):
    return render(request, 'goals/goal_confirm_delete.html')
