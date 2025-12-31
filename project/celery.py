"""
Configuración de Celery para Django.

Este módulo configura Celery como la cola de tareas asincrónicas,
utilizando Redis como broker y también como backend de resultados.
"""

import os

from celery import Celery

# Establecer el módulo de configuración de Django por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Crear la aplicación Celery
app = Celery('template_filler')

# Cargar la configuración desde Django settings
# El namespace='CELERY' significa que todas las configuraciones de Celery
# en settings.py deben estar prefijadas con CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubrir automáticamente tareas desde todos los módulos tasks.py
# de las aplicaciones registradas
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    Tarea de debug para verificar que Celery está funcionando correctamente.
    """
    print(f'Request: {self.request!r}')
