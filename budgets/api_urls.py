from rest_framework.routers import DefaultRouter
from .views.api import BudgetViewSet

router = DefaultRouter()
router.register('budgets', BudgetViewSet, basename='api-budget')
urlpatterns = router.urls
