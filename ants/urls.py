from django.urls import path
from .views import pages

app_name = 'ants'

urlpatterns = [
    path('ants/colony/', pages.colony_view, name='colony_view'),
]
