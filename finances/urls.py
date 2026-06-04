from django.urls import path
from .views import pages

app_name = 'finances'

urlpatterns = [
    path('', pages.dashboard, name='dashboard'),
    path('transactions/', pages.transaction_list, name='transaction_list'),
    path('transactions/add/', pages.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', pages.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', pages.transaction_delete, name='transaction_delete'),
    path('incomes/', pages.income_list, name='income_list'),
    path('expenses/', pages.expense_list, name='expense_list'),
    path('categories/', pages.category_list, name='category_list'),
]
