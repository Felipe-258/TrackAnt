from django.urls import path
from .views import welcome, login_view, registro, logout_view
from .views.settings import settings_view, backup_download_view

app_name = 'users'

urlpatterns = [
    path('welcome/', welcome, name='welcome'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro, name='registro'),
    path('settings/', settings_view, name='settings'),
    path('settings/backup/', backup_download_view, name='backup_download'),
]
