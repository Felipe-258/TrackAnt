from rest_framework import viewsets
from ..models import Reserve
from ..serializers import ReserveSerializer


class ReserveViewSet(viewsets.ModelViewSet):
    serializer_class = ReserveSerializer
    filterset_fields = ['is_achieved']
    ordering_fields = ['deadline', 'created_at']
    ordering = ['is_achieved', 'deadline']

    def get_queryset(self):
        return Reserve.objects.filter(colony=self.request.colony).select_related('currency')

    def perform_create(self, serializer):
        serializer.save(colony=self.request.colony)
