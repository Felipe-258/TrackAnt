from rest_framework.routers import DefaultRouter
from .views.api import DebtViewSet, DebtPaymentViewSet

router = DefaultRouter()
router.register('debts', DebtViewSet, basename='api-debt')
router.register('debt-payments', DebtPaymentViewSet, basename='api-debtpayment')
urlpatterns = router.urls
