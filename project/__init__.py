"""
Inicialización de la aplicación Django.

Asegura que Celery se carga cuando Django se inicia.
"""

# Importar la aplicación Celery para inicializarla
from .celery import app as celery_app

__all__ = ['celery_app']
