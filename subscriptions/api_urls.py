from rest_framework.routers import DefaultRouter
from .views.api import SubscriptionViewSet

router = DefaultRouter()
router.register('subscriptions', SubscriptionViewSet, basename='api-subscription')
urlpatterns = router.urls
