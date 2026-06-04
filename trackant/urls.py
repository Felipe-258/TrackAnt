from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('finances.urls')),
    path('', include('goals.urls')),
    path('', include('debts.urls')),
    path('', include('budgets.urls')),
    path('', include('subscriptions.urls')),
    path('', include('splits.urls')),
    path('api/v1/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
