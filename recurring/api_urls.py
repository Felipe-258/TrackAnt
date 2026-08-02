from rest_framework.routers import DefaultRouter
from .views.api import RecurringTransactionViewSet

router = DefaultRouter()
router.register('recurring-transactions', RecurringTransactionViewSet, basename='api-recurring-transaction')
urlpatterns = router.urls
