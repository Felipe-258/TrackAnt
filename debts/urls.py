from django.urls import path
from .views import pages

app_name = 'debts'

urlpatterns = [
    path('debts/', pages.debt_list, name='debt_list'),
    path('debts/add/', pages.debt_add, name='debt_add'),
    path('debts/<int:pk>/', pages.debt_detail, name='debt_detail'),
    path('debts/<int:pk>/edit/', pages.debt_edit, name='debt_edit'),
    path('debts/<int:pk>/delete/', pages.debt_delete, name='debt_delete'),
]
