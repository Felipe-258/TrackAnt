from django.urls import path
from .views import pages

app_name = 'installments'

urlpatterns = [
    path('cuotas/', pages.installment_list, name='list'),
    path('cuotas/add/', pages.installment_add, name='add'),
    path('cuotas/<int:pk>/', pages.installment_detail, name='detail'),
    path('cuotas/<int:pk>/edit/', pages.installment_edit, name='edit'),
    path('cuotas/<int:pk>/delete/', pages.installment_delete, name='delete'),
    path('cuotas/<int:pk>/pay/', pages.installment_pay, name='pay'),
    path('cuotas/<int:pk>/unpay/', pages.installment_unpay, name='unpay'),
]
