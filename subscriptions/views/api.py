from rest_framework import viewsets
from ..models import Subscription
from ..serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.select_related('currency', 'category')
    serializer_class = SubscriptionSerializer
    filterset_fields = ['is_active', 'cycle']
    ordering = ['next_date']
