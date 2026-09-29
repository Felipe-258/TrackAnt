from django.urls import path
from .views import pages

app_name = 'splits'

urlpatterns = [
    path('splits/', pages.split_list, name='split_list'),
    path('splits/groups/add/', pages.split_group_add, name='split_group_add'),
    path('splits/groups/<int:pk>/', pages.split_group_detail, name='split_group_detail'),
    path('splits/groups/<int:pk>/edit/', pages.split_group_edit, name='split_group_edit'),
    path('splits/groups/<int:pk>/delete/', pages.split_group_delete, name='split_group_delete'),
    path('splits/expenses/add/<int:group_id>/', pages.split_expense_add, name='split_expense_add'),
    path('splits/expenses/<int:pk>/edit/', pages.split_expense_edit, name='split_expense_edit'),
    path('splits/expenses/<int:pk>/delete/', pages.split_expense_delete, name='split_expense_delete'),
    path('splits/groups/<int:pk>/pay/', pages.split_payment_add, name='split_payment_add'),
    path('splits/payments/<int:pk>/delete/', pages.split_payment_delete, name='split_payment_delete'),
    path('splits/groups/<int:pk>/preference/', pages.split_preference_add, name='split_preference_add'),
    path('splits/groups/<int:pk>/preference/remove/', pages.split_preference_remove, name='split_preference_remove'),
]
