"""
IURL configuration for the 'docs' app.

Defines URL patterns for uploading documents, checking status,
downloading generated documents, and managing document jobs.
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'documentos'

urlpatterns = [
    # Upload of documents
    path('upload/', csrf_exempt(views.UploadView.as_view()), name='upload'),
    
    # Status check of document job
    path('status/<uuid:job_id>/', views.StatusView.as_view(), name='status'),
    
    # Download generated document
    path('download/<uuid:job_id>/', views.DownloadView.as_view(), name='download'),
    
    # Delete document job
    path('delete/<uuid:job_id>/', csrf_exempt(views.DeleteJobView.as_view()), name='delete'),
    
    # List all document jobs
    path('jobs/', views.ListJobsView.as_view(), name='jobs_list'),
]
