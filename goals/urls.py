from django.urls import path
from .views import pages

app_name = 'goals'

urlpatterns = [
    path('goals/', pages.goal_list, name='goal_list'),
    path('goals/add/', pages.goal_add, name='goal_add'),
    path('goals/<int:pk>/edit/', pages.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/delete/', pages.goal_delete, name='goal_delete'),
]
