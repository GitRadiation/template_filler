"""
Initialize the project package.

Ensures that the Celery application is loaded when Django starts.
"""

# Import the Celery application instance
from .celery import app as celery_app

__all__ = ['celery_app']
