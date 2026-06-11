from rest_framework import viewsets
from ..models import Goal
from ..serializers import GoalSerializer


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    filterset_fields = ['is_achieved']
    ordering_fields = ['deadline', 'created_at']
    ordering = ['is_achieved', 'deadline']

    def get_queryset(self):
        return Goal.objects.filter(colony=self.request.colony).select_related('currency')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)
