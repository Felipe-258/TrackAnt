from rest_framework.routers import DefaultRouter
from .views.api import GoalViewSet

router = DefaultRouter()
router.register('goals', GoalViewSet, basename='api-goal')
urlpatterns = router.urls
