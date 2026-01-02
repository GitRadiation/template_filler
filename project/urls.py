"""
URLs from project Template Filler.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # For language switching
]

urlpatterns += i18n_patterns(path('', RedirectView.as_view(url='api/docs/upload/', permanent=False), name='home'),
    path('admin/', admin.site.urls),
    path('api/docs/', include('docs.urls')),)

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/generated/', document_root=settings.GENERATED_DOCUMENTS_DIR)
