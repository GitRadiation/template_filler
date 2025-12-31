"""
Configuración de Django para producción/desarrollo local.

Este archivo proporciona un punto de entrada para WSGI compatible
con servidores como Gunicorn y similares.
"""

import os
from pathlib import Path

# Establecer el módulo de configuración
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Asegurarse de que el directorio está en el path de Python
if str(BASE_DIR) not in os.sys.path:
    os.sys.path.insert(0, str(BASE_DIR))

# Obtener la aplicación WSGI
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
