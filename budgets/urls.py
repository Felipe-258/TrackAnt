from django.urls import path
from .views import pages

app_name = 'budgets'

urlpatterns = [
    path('budgets/', pages.budget_list, name='budget_list'),
    path('budgets/add/', pages.budget_add, name='budget_add'),
    path('budgets/<int:pk>/edit/', pages.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', pages.budget_delete, name='budget_delete'),
]
