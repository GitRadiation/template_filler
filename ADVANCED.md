# ⚙️ Configuraciones Avanzadas - Template Filler

Guía para configurar opciones avanzadas, optimizaciones y extensiones.

---

## 🔧 Configuración de Celery Avanzada

### Beat (Tareas Programadas)

**1. Instalar Beat Scheduler:**

```bash
poetry add celery-beat
```

**2. Agregar en `project/settings.py`:**

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-documents': {
        'task': 'documentos.tasks.cleanup_old_documents',
        'schedule': crontab(hour=2, minute=0),  # 2 AM diariamente
    },
    'generate-daily-report': {
        'task': 'documentos.tasks.generate_daily_report',
        'schedule': crontab(hour=8, minute=0),  # 8 AM diariamente
    },
}
```

**3. Crear tareas en `documentos/tasks.py`:**

```python
@shared_task
def cleanup_old_documents():
    """Elimina documentos generados hace más de 30 días."""
    from datetime import timedelta
    from django.utils import timezone
    
    cutoff_date = timezone.now() - timedelta(days=30)
    jobs = DocumentJob.objects.filter(
        completed_at__lt=cutoff_date,
        status='completed'
    )
    
    for job in jobs:
        if job.output_file:
            job.output_file.delete()
        job.delete()
    
    logger.info(f'Limpiezas: {jobs.count()} documentos eliminados')


@shared_task
def generate_daily_report():
    """Genera reporte diario de documentos."""
    from django.utils import timezone
    from datetime import timedelta
    
    yesterday = timezone.now() - timedelta(days=1)
    
    stats = {
        'total': DocumentJob.objects.filter(created_at__date=yesterday.date()).count(),
        'completed': DocumentJob.objects.filter(
            created_at__date=yesterday.date(),
            status='completed'
        ).count(),
        'failed': DocumentJob.objects.filter(
            created_at__date=yesterday.date(),
            status='failed'
        ).count(),
    }
    
    logger.info(f'Reporte diario: {stats}')
    return stats
```

**4. Iniciar Beat:**

```bash
# Local
poetry run celery -A project beat --loglevel=info

# Con Scheduler persistente
poetry run celery -A project beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**5. En Docker Compose:**

```yaml
beat:
  build: .
  command: celery -A project beat --loglevel=info
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
    - CELERY_RESULT_BACKEND=redis://redis:6379/1
  depends_on:
    redis:
      condition: service_healthy
  volumes:
    - .:/app
  restart: on-failure
```

---

### Implementar Priority Queues

**1. En `project/settings.py`:**

```python
CELERY_TASK_ROUTES = {
    'documentos.tasks.generate_pdf_task': {
        'queue': 'documents',
        'priority': 9,  # Alta prioridad
    },
    'documentos.tasks.cleanup_task': {
        'queue': 'background',
        'priority': 1,  # Baja prioridad
    },
}

CELERY_QUEUES = {
    'documents': {
        'exchange': 'documents',
        'binding_key': 'documents',
        'priority': 10,
    },
    'background': {
        'exchange': 'background',
        'binding_key': 'background',
        'priority': 1,
    },
    'default': {
        'exchange': 'default',
        'binding_key': 'default',
        'priority': 5,
    },
}
```

**2. Ejecutar workers con soporte a prioridades:**

```bash
poetry run celery -A project worker \
  -Q documents,default,background \
  -l info \
  --time-limit=3600 \
  --soft-time-limit=3000
```

---

## 🔐 Seguridad

### HTTPS en Producción

**1. Configurar SSL en `project/settings.py`:**

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**2. Con Nginx + Certbot:**

```nginx
server {
    listen 443 ssl http2;
    server_name tudominio.com;
    
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/staticfiles/;
    }
    
    location /media/ {
        alias /app/media/;
    }
}
```

---

### Autenticación con Token

**1. Instalar Django REST Framework:**

```bash
poetry add djangorestframework
```

**2. En `project/settings.py`:**

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

**3. Crear vista con autenticación en `documentos/views.py`:**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def secure_upload(request):
    """Subida de documento requiere autenticación."""
    # Código de upload aquí
    pass
```

**4. Usar Token:**

```bash
# Generar token
TOKEN=$(curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.token')

# Usar en peticiones
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/documentos/upload/
```

---

## 📊 Bases de Datos

### Backup y Restore Automatizado

**1. Script de backup `scripts/backup.sh`:**

```bash
#!/bin/bash

BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
docker-compose exec -T db pg_dump -U djangouser djangodb > "$BACKUP_FILE"

# Comprimir
gzip "$BACKUP_FILE"

# Limpiar backups antiguos (>30 días)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup creado: ${BACKUP_FILE}.gz"
```

**2. Script de restauración `scripts/restore.sh`:**

```bash
#!/bin/bash

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Uso: ./restore.sh backup.sql.gz"
    exit 1
fi

# Descomprimir si es necesario
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U djangouser djangodb
else
    cat "$BACKUP_FILE" | docker-compose exec -T db psql -U djangouser djangodb
fi

echo "Restauración completada"
```

**3. Backup automático diario con cron:**

```bash
# crontab -e
0 2 * * * cd /app && ./scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

### Replicación con Streaming

**1. Configurar replicación en `docker-compose.yml`:**

```yaml
db-primary:
  image: bitnami/postgresql:17
  environment:
    - POSTGRESQL_REPLICATION_MODE=master
    - POSTGRESQL_REPLICATION_USER=replicator
    - POSTGRESQL_REPLICATION_PASSWORD=repl_password
  volumes:
    - db_data_primary:/bitnami/postgresql

db-replica:
  image: bitnami/postgresql:17
  environment:
    - POSTGRESQL_REPLICATION_MODE=slave
    - POSTGRESQL_MASTER_SERVICE=db-primary
    - POSTGRESQL_REPLICATION_USER=replicator
    - POSTGRESQL_REPLICATION_PASSWORD=repl_password
  depends_on:
    - db-primary
  volumes:
    - db_data_replica:/bitnami/postgresql
```

---

## 🎯 Performance & Caching

### Redis Caching

**1. En `project/settings.py`:**

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
    }
}

# Cache de vistas
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
```

**2. Cache en vistas:**

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache 5 minutos
def status_view(request, job_id):
    return status_response(...)
```

---

### Compresión de Respuestas

**1. En `project/settings.py`:**

```python
MIDDLEWARE = [
    ...
    'django.middleware.gzip.GZipMiddleware',
    ...
]
```

---

## 🐳 Docker Avanzado

### Multi-stage Build

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry export -f requirements.txt | pip install -r /dev/stdin

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Copiar solo dependencias del stage anterior
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY . .

EXPOSE 8000
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

### Health Checks Personalizados

```yaml
services:
  web:
    healthcheck:
      test: |
        curl -f http://localhost:8000/admin/ &&
        python -c "
        import django; django.setup();
        from django.db import connection;
        connection.ensure_connection()
        " || exit 1
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 📈 Monitoreo Avanzado

### Prometheus Metrics

**1. Instalar:**

```bash
poetry add prometheus-client django-prometheus
```

**2. En `project/settings.py`:**

```python
INSTALLED_APPS = [
    ...
    'django_prometheus',
    ...
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusMiddleware',
    ...
]
```

**3. URLs:**

```python
urlpatterns = [
    ...
    path('metrics/', include('django_prometheus.urls')),
]
```

**4. Acceder:**

```
http://localhost:8000/metrics/
```

---

### Sentry para Error Tracking

**1. Instalar:**

```bash
poetry add sentry-sdk
```

**2. En `project/settings.py`:**

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    traces_sample_rate=0.1,
    environment="production",
)
```

---

## 🚀 Despliegue en Producción

### Con Gunicorn + Systemd

**1. Crear servicio `/etc/systemd/system/template-filler.service`:**

```ini
[Unit]
Description=Template Filler Django App
After=network.target

[Service]
Type=notify
User=django
WorkingDirectory=/app
Environment="PATH=/app/.venv/bin"
ExecStart=/app/.venv/bin/gunicorn \
    project.wsgi:application \
    --bind unix:/run/template-filler.sock \
    --workers 4 \
    --worker-class gthread \
    --threads 2 \
    --timeout 60

[Install]
WantedBy=multi-user.target
```

**2. Iniciar:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable template-filler
sudo systemctl start template-filler
```

---

### Con Kubernetes

**1. Crear `k8s/deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: template-filler
spec:
  replicas: 3
  selector:
    matchLabels:
      app: template-filler
  template:
    metadata:
      labels:
        app: template-filler
    spec:
      containers:
      - name: web
        image: template-filler:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_HOST
          value: postgres-service
        - name: CELERY_BROKER_URL
          value: redis://redis-service:6379/0
```

---

## 🔄 Migraciones Avanzadas

### Migración Cero-Downtime

```python
# 1. Agregar campo con default
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='documentjob',
            name='new_field',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
    ]

# 2. Llenar datos en background
# 3. Cambiar lógica de aplicación
# 4. Eliminar campo antiguo en siguiente migración
```

---

## 📚 Extensiones Útiles

### Agregar Soporte para S3

**1. Instalar:**

```bash
poetry add django-storages boto3
```

**2. Configurar en `project/settings.py`:**

```python
if not DEBUG:
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'AWS_STORAGE_BUCKET_NAME': 'template-filler-docs',
                'AWS_S3_REGION_NAME': 'us-east-1',
            }
        }
    }
```

---

### GraphQL API

**1. Instalar:**

```bash
poetry add graphene-django
```

**2. Crear `documentos/schema.py`:**

```python
import graphene
from .models import DocumentJob

class DocumentJobType(graphene.ObjectType):
    id = graphene.ID()
    template_name = graphene.String()
    status = graphene.String()

class Query(graphene.ObjectType):
    all_jobs = graphene.List(DocumentJobType)
    job(id=graphene.ID()) = graphene.Field(DocumentJobType)

class Mutation(graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
```

---

**Última actualización:** Enero 2025
