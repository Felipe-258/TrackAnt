from rest_framework.routers import DefaultRouter
from .views.api import InstallmentPurchaseViewSet, InstallmentViewSet

router = DefaultRouter()
router.register('installment-purchases', InstallmentPurchaseViewSet, basename='api-installment-purchase')
router.register('installments', InstallmentViewSet, basename='api-installment')
urlpatterns = router.urls
