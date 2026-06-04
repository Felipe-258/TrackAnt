from rest_framework.routers import DefaultRouter
from .views.api import SplitGroupViewSet, SplitExpenseViewSet

router = DefaultRouter()
router.register('split-groups', SplitGroupViewSet, basename='api-splitgroup')
router.register('split-expenses', SplitExpenseViewSet, basename='api-splitexpense')
urlpatterns = router.urls
