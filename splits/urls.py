from django.urls import path
from .views import pages

app_name = 'splits'

urlpatterns = [
    path('splits/', pages.split_list, name='split_list'),
    path('splits/groups/add/', pages.split_group_add, name='split_group_add'),
    path('splits/expenses/add/<int:group_id>/', pages.split_expense_add, name='split_expense_add'),
]
