from rest_framework.routers import DefaultRouter
from .views.api import ReserveViewSet

router = DefaultRouter()
router.register('reserves', ReserveViewSet, basename='api-reserve')
urlpatterns = router.urls
