from django.urls import path
from .views import pages

app_name = 'recurring'

urlpatterns = [
    path('recurrentes/', pages.recurring_list, name='list'),
    path('recurrentes/add/', pages.recurring_add, name='add'),
    path('recurrentes/<int:pk>/edit/', pages.recurring_edit, name='edit'),
    path('recurrentes/<int:pk>/delete/', pages.recurring_delete, name='delete'),
]
