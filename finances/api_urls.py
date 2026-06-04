from rest_framework.routers import DefaultRouter
from .views.api import CurrencyViewSet, CategoryViewSet, TagViewSet, TransactionViewSet

router = DefaultRouter()
router.register('currencies', CurrencyViewSet, basename='api-currency')
router.register('categories', CategoryViewSet, basename='api-category')
router.register('tags', TagViewSet, basename='api-tag')
router.register('transactions', TransactionViewSet, basename='api-transaction')
urlpatterns = router.urls
