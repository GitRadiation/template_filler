"""
URLs del proyecto Template Filler.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='api/documentos/upload/', permanent=False), name='home'),
    path('admin/', admin.site.urls),
    path('api/documentos/', include('documentos.urls')),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/generated/', document_root=settings.GENERATED_DOCUMENTS_DIR)
