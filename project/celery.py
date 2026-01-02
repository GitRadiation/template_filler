"""
Celery configuration for Django.

This module configures Celery as the asynchronous task queue,
using Redis as the broker and also as the result backend.
"""

import os

from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Create the Celery application
app = Celery('template_filler')

# Load configuration from Django settings
# The namespace='CELERY' means that all Celery-related settings
# in settings.py must be prefixed with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all tasks.py modules
# in registered Django applications
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    Debug task to verify that Celery is working correctly.
    """
    print(f'Request: {self.request!r}')
