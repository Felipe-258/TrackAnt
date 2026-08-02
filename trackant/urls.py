from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView
import os


def service_worker(request):
    sw_path = os.path.join(settings.STATICFILES_DIRS[0], 'sw.js')
    with open(sw_path, 'r') as f:
        return HttpResponse(f.read(), content_type='application/javascript')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker, name='service_worker'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('', include('users.urls')),
    path('', include('finances.urls')),
    path('', include('goals.urls')),
    path('', include('debts.urls')),
    path('', include('budgets.urls')),
    path('', include('subscriptions.urls')),
    path('', include('installments.urls')),
    path('', include('recurring.urls')),
    path('', include('splits.urls')),
    path('', include('ants.urls')),
    path('api/v1/', include('api.urls')),
]

if settings.DEBUG:
    from ants.views.pages import playground
    urlpatterns.insert(0, path('ants/playground/', playground, name='playground'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
