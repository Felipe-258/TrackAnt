from rest_framework.routers import DefaultRouter
from django.urls import path
from .views.api import CurrencyViewSet, CategoryViewSet, TagViewSet, TransactionViewSet, api_rates

router = DefaultRouter()
router.register('currencies', CurrencyViewSet, basename='api-currency')
router.register('categories', CategoryViewSet, basename='api-category')
router.register('tags', TagViewSet, basename='api-tag')
router.register('transactions', TransactionViewSet, basename='api-transaction')
urlpatterns = router.urls + [path('rates/', api_rates, name='api-rates')]
