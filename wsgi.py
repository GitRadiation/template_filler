"""
Django configuration for production/local development.

This file provides an entry point for WSGI compatible
with servers such as Gunicorn and similar ones.
"""

import os
from pathlib import Path

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Ensure the directory is in the Python path
if str(BASE_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(BASE_DIR))

# Get the WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
