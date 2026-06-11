from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('finances.urls')),
    path('', include('goals.urls')),
    path('', include('debts.urls')),
    path('', include('budgets.urls')),
    path('', include('subscriptions.urls')),
    path('', include('splits.urls')),
    path('', include('ants.urls')),
    path('api/v1/', include('api.urls')),
]

if settings.DEBUG:
    from ants.views.pages import playground
    urlpatterns.insert(0, path('ants/playground/', playground, name='playground'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
