from django.urls import path
from .views import welcome, login_view, registro, logout_view, settings_view

app_name = 'users'

urlpatterns = [
    path('welcome/', welcome, name='welcome'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro, name='registro'),
    path('settings/', settings_view, name='settings'),
]
