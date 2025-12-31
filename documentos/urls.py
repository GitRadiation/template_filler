"""
URLs de la aplicación documentos.

Define las rutas para:
- Subida de documentos
- Consulta de estado
- Descarga de archivos
- Listado de trabajos
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'documentos'

urlpatterns = [
    # Formulario y procesamiento de subida
    path('upload/', csrf_exempt(views.UploadView.as_view()), name='upload'),
    
    # Consulta de estado
    path('status/<uuid:job_id>/', views.StatusView.as_view(), name='status'),
    
    # Descarga de documento
    path('download/<uuid:job_id>/', views.DownloadView.as_view(), name='download'),
    
    # Listado de trabajos (debugging)
    path('jobs/', views.ListJobsView.as_view(), name='jobs_list'),
]
