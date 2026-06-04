from django.urls import path
from .views import pages

app_name = 'subscriptions'

urlpatterns = [
    path('subscriptions/', pages.subscription_list, name='subscription_list'),
    path('subscriptions/add/', pages.subscription_add, name='subscription_add'),
    path('subscriptions/<int:pk>/edit/', pages.subscription_edit, name='subscription_edit'),
    path('subscriptions/<int:pk>/delete/', pages.subscription_delete, name='subscription_delete'),
]
