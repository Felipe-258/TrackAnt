from rest_framework import viewsets
from ..models import Goal
from ..serializers import GoalSerializer


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.select_related('currency')
    serializer_class = GoalSerializer
    filterset_fields = ['is_achieved']
    ordering_fields = ['deadline', 'created_at']
    ordering = ['is_achieved', 'deadline']
