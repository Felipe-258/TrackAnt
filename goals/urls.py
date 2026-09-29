from django.urls import path
from .views import pages

app_name = 'reserves'

urlpatterns = [
    path('reservas/', pages.reserve_list, name='list'),
    path('reservas/add/', pages.reserve_add, name='add'),
    path('reservas/<int:pk>/edit/', pages.reserve_edit, name='edit'),
    path('reservas/<int:pk>/delete/', pages.reserve_delete, name='delete'),
    path('reservas/<int:pk>/deposit/', pages.reserve_deposit, name='deposit'),
    path('reservas/<int:pk>/withdraw/', pages.reserve_withdraw, name='withdraw'),
]
