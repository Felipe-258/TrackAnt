from rest_framework.routers import DefaultRouter
from .views.api import SubscriptionViewSet, SubscriptionPaymentViewSet

router = DefaultRouter()
router.register('subscriptions', SubscriptionViewSet, basename='api-subscription')
router.register('subscription-payments', SubscriptionPaymentViewSet, basename='api-subscription-payment')
urlpatterns = router.urls
