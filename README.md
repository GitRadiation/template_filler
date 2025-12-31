# 📄 Template Filler - Generador Completo de Documentos

Sistema completo para generar documentos profesionales (PDF, DOCX, JSON) utilizando plantillas Jinja2, Django, Celery y Redis. Incluye interfaz drag-and-drop, procesamiento asincrónico y monitoreo en tiempo real.

---

## 📦 Requisitos

### Local

- Python 3.12+
- Poetry
- PostgreSQL 15+
- Redis 7+
- LibreOffice/WeasyPrint dependencies

### Docker

- Docker
- Podman-compose (o docker-compose)

---

## 🚀 Instalacion Local

### 1. Clonar y configurar

```bash
cd /home/user/UNIVERSIDAD/template_filler
```text

### 2. Crear archivo `.env` (Opcional, para valores por defecto)

```bash
cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=djangodb
DATABASE_USER=djangouser
DATABASE_PASSWORD=secretpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
```text

### 3. Instalar dependencias con Poetry

```bash
poetry install
```text

### 4. Configurar PostgreSQL

```bash
# Crear base de datos
createdb -U postgres djangodb

# Crear usuario
psql -U postgres -d djangodb -c "CREATE USER djangouser WITH PASSWORD 'secretpassword';"

# Otorgar permisos
psql -U postgres -d djangodb -c "GRANT ALL PRIVILEGES ON DATABASE djangodb TO djangouser;"
```text

### 5. Iniciar Redis

```bash
redis-server
# O en otra terminal:
# redis-cli
```text

### 6. Migraciones Django

```bash
poetry run python manage.py migrate
```text

### 7. Crear superusuario

```bash
poetry run python manage.py createsuperuser
```text

### 8. Crear directorios necesarios

```bash
mkdir -p generated uploads media staticfiles
```text

### 9. Ejecutar servidor Django

```bash
poetry run python manage.py runserver
# Accesible en: http://localhost:8000
```text

### 10. Ejecutar worker Celery (en otra terminal)

```bash
poetry run celery -A project worker --loglevel=info
```text

### 11. (Opcional) Ejecutar Flower para monitoreo

```bash
poetry run celery -A project flower
# Accesible en: http://localhost:5555
```text

---

## 🐳 Instalacion con Docker

### 1. Construir imágenes

```bash
docker-compose build
```text

### 2. Iniciar servicios

```bash
docker-compose up -d
```text

Esto iniciará:
- **PostgreSQL** en puerto 5432
- **Redis** en puerto 6379
- **Django Web** en puerto 8000
- **Celery Worker** procesando tareas
- **Flower** (monitoreo) en puerto 5555

### 3. Verificar que está funcionando

```bash
# Ver logs
docker-compose logs -f web

# Verificar salud de servicios
docker-compose ps

# Acceder a la aplicación
curl http://localhost:8000
```text

### 4. Crear superusuario (si no se creó automáticamente)

```bash
docker-compose exec web python manage.py createsuperuser
```text

### 5. Detener servicios

```bash
docker-compose down

# Para borrar volúmenes (CUIDADO - borra datos):
docker-compose down -v
```text

---

## 📁 Estructura del Proyecto

```text
template_filler/
├── project/                    # Configuración de Django
│   ├── __init__.py
│   ├── settings.py             # Configuración completa (incluye Celery)
│   ├── urls.py                 # URLs raíz
│   ├── wsgi.py                 # Entry point WSGI
│   ├── asgi.py                 # Entry point ASGI
│   └── celery.py               # Configuración de Celery
│
├── documentos/                 # Aplicación principal
│   ├── models.py               # DocumentJob model
│   ├── views.py                # UploadView, StatusView, DownloadView
│   ├── urls.py                 # Rutas /upload/, /status/, /download/
│   ├── services.py             # DocumentService (lógica de negocio)
│   ├── tasks.py                # Tareas Celery (generate_pdf, generate_docx, etc)
│   ├── admin.py                # Admin Django
│   ├── apps.py                 # Configuración de app
│   ├── templates/
│   │   └── documentos/
│   │       └── upload.html     # Interfaz drag-and-drop
│   ├── migrations/
│   │   └── __init__.py
│   └── management/
│       └── commands/
│           └── retry_failed_jobs.py  # Comando para reintentar trabajos
│
├── templates_doc/              # Plantillas Jinja2
│   ├── contract.html.j2        # Plantilla de contrato
│   ├── invoice.html.j2         # Plantilla de factura
│   └── certificate.html.j2     # Plantilla de certificado
│
├── generated/                  # Documentos generados (PDFs)
├── uploads/                    # Archivos cargados por usuarios
├── media/                      # Archivos multimedia
├── staticfiles/                # CSS, JS estático
│
├── docker-compose.yml          # Orquestación Docker
├── Dockerfile                  # Imagen Docker
├── manage.py                   # Entry point Django
├── pyproject.toml              # Dependencias Poetry
├── example_contract.json       # Ejemplo: entrada para contrato
├── example_invoice.json        # Ejemplo: entrada para factura
├── example_certificate.json    # Ejemplo: entrada para certificado
└── README.md                   # Este archivo
```text

---

## ⚙️ Configuracion de Celery

### Broker y Backend

**Broker** (transporte de mensajes): Redis
```text
redis://localhost:6379/0
```text

**Backend** (almacenamiento de resultados): Redis
```text
redis://localhost:6379/1
```text

### Colas Configuradas

```python
CELERY_QUEUES = {
    'default': { ... },      # Tareas genéricas
    'documents': { ... },    # Tareas de documentos
}
```text

### Rutas de Tareas

```python
CELERY_TASK_ROUTES = {
    'documentos.tasks.generate_pdf_task': {'queue': 'documents'},
    'documentos.tasks.generate_docx_task': {'queue': 'documents'},
    'documentos.tasks.generate_json_task': {'queue': 'documents'},
}
```text

### Configuración de Reintentos

```python
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # segundos
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutos
```text

### Ejecutar Worker

**Local con Poetry:**
```bash
poetry run celery -A project worker --loglevel=info
```text

**Local con workers específicos:**
```bash
# Worker para cola 'documents'
poetry run celery -A project worker -Q documents --loglevel=info

# Múltiples workers
poetry run celery -A project worker -Q default,documents --concurrency=4
```text

**Docker:**
```bash
docker-compose up worker
```text

---

## 🔌 API Endpoints

### 1. Subir Documento (GET/POST)
```text
GET /api/documentos/upload/
POST /api/documentos/upload/
```text

**Respuesta POST exitosa (201):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Documento en proceso de generación"
}
```text

**Parámetros POST:**
- `template_name` (required): 'contract' | 'invoice' | 'certificate'
- `file` (required): Archivo JSON con datos

**Ejemplo con cURL:**
```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"
```text

---

### 2. Consultar Estado
```text
GET /api/documentos/status/<job_id>/
```text

**Respuesta:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "template_name": "contract",
  "created_at": "2025-01-15T10:30:00Z",
  "started_at": "2025-01-15T10:30:05Z",
  "completed_at": null,
  "error_message": null,
  "output_url": null
}
```text

**Estados posibles:**
- `pending`: Esperando procesamiento
- `running`: En proceso
- `completed`: Completado exitosamente
- `failed`: Error durante la generación

**Ejemplo:**
```bash
curl http://localhost:8000/api/documentos/status/550e8400-e29b-41d4-a716-446655440000/
```text

---

### 3. Descargar Documento
```text
GET /api/documentos/download/<job_id>/
```text

**Respuesta:** Archivo PDF descargado

**Ejemplo:**
```bash
curl -o documento.pdf http://localhost:8000/api/documentos/download/550e8400-e29b-41d4-a716-446655440000/
```text

---

### 4. Listar Trabajos (Debugging)
```text
GET /api/documentos/jobs/
```text

**Parámetros opcionales:**
- `status`: 'pending' | 'running' | 'completed' | 'failed'
- `template`: 'contract' | 'invoice' | 'certificate'
- `limit`: Número máximo (default: 50)

**Ejemplo:**
```bash
curl "http://localhost:8000/api/documentos/jobs/?status=completed&limit=10"
```text

---

## 📋 Ejemplos de Uso

### Ejemplo 1: Generar Contrato

**1. Preparar datos JSON:**
```bash
cat > datos_contrato.json << 'EOF'
{
  "contracting_party_name": "Empresa ABC SpA",
  "contracting_party_id": "12.345.678-9",
  "contracting_party_address": "Calle Principal 123, Santiago",
  "contractor_name": "Juan Pérez García",
  "contractor_id": "98.765.432-1",
  "contractor_address": "Avenida Secundaria 456, Santiago",
  "contract_object": "Servicios de consultoría empresarial",
  "start_date": "01/01/2025",
  "end_date": "31/12/2025",
  "duration": "12 meses",
  "services": [
    {
      "description": "Consultoría Fase I",
      "unit_price": "5000000",
      "quantity": 1,
      "total": "5000000"
    }
  ],
  "total_amount": "5000000",
  "payment_method": "Transferencia bancaria",
  "terms_and_conditions": "Ambas partes acuerdan..."
}
EOF
```text

**2. Enviar al servidor:**
```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@datos_contrato.json"
```text

**3. Respuesta:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```text

**4. Verificar estado:**
```bash
curl http://localhost:8000/api/documentos/status/550e8400-e29b-41d4-a716-446655440000/
```text

**5. Descargar cuando esté completado:**
```bash
curl -o contrato.pdf \
  http://localhost:8000/api/documentos/download/550e8400-e29b-41d4-a716-446655440000/
```text

---

### Ejemplo 2: Usar interfaz Web (Drag & Drop)

**1. Abrir en navegador:**
```text
http://localhost:8000/api/documentos/upload/
```text

**2. Pasos:**
   - Seleccionar tipo de plantilla (Contrato, Factura, Certificado)
   - Arrastrar archivo JSON o hacer clic para seleccionar
   - Hacer clic en "Generar Documento"
   - Esperar a que complete
   - Descargar PDF

---

### Ejemplo 3: Generar Factura

```bash
# 1. Con archivo
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=invoice" \
  -F "file=@example_invoice.json"

# 2. Con JSON directo (POST form data)
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=invoice" \
  -F "data={\"company_name\": \"Tech Solutions S.A.\", ...}"
```text

---

### Ejemplo 4: Reintentar Trabajos Fallidos

```bash
# Reintentar últimos 10 trabajos fallidos
poetry run python manage.py retry_failed_jobs --limit 10

# Reintentar trabajos de últimas 24 horas
poetry run python manage.py retry_failed_jobs --hours 24
```text

---

### Ejemplo 5: Panel Administrativo

**1. Acceder:**
```text
http://localhost:8000/admin/
```text

**2. Credenciales (por defecto con Docker):**
- Usuario: `admin`
- Contraseña: `admin123`

**3. Funciones:**
   - Ver todos los trabajos de documentos
   - Filtrar por estado, plantilla, fecha
   - Reintentar trabajos fallidos (botón de acción)
   - Marcar como pendiente
   - Descargar documentos generados

---

## 📊 Monitoreo con Flower

**Acceder a Flower:**
```text
http://localhost:5555
```text

**Características:**
- Monitor en tiempo real de workers
- Historial de tareas
- Estadísticas por segundo
- Cancelar tareas
- Pool management
- Gráficos de desempeño

**Comandos útiles:**

```bash
# Iniciar Flower (local)
poetry run celery -A project flower

# Con puerto personalizado
poetry run celery -A project flower --port=5556

# Con persistencia de datos
poetry run celery -A project flower --persistent=True --db=flower.db
```text

---

## 🔍 Troubleshooting

### Problema: "No se ha podido resolver la importación 'decouple'"

**Solución:**
```bash
poetry install
# O instalar manualmente:
pip install python-decouple
```text

---

### Problema: Celery no procesa tareas

**Verificar:**

```bash
# 1. Redis está corriendo
redis-cli ping
# Debe retornar: PONG

# 2. Worker está ejecutándose
poetry run celery -A project worker --loglevel=debug

# 3. Cola está configurada correctamente
# Ver en project/settings.py: CELERY_BROKER_URL
```text

---

### Problema: Base de datos no existe

**Solución:**
```bash
# PostgreSQL
createdb -U postgres djangodb
psql -U postgres -d djangodb -c "CREATE USER djangouser WITH PASSWORD 'secretpassword';"

# Luego migrar
poetry run python manage.py migrate
```text

---

### Problema: Puerto 8000 ya está en uso

**Solución:**
```bash
# Usar puerto diferente
poetry run python manage.py runserver 0.0.0.0:8080

# O liberar puerto
lsof -i :8000
kill -9 <PID>
```text

---

### Problema: WeasyPrint no genera PDF

**Verificar dependencias:**
```bash
# En Ubuntu/Debian
sudo apt-get install libffi-dev libcairo2-dev libpango1.0-dev libpangoft2-1.0-0

# En macOS
brew install libffi cairo pango gdk-pixbuf

# Reinstalar WeasyPrint
pip install --force-reinstall WeasyPrint
```text

---

### Problema: Tareas quedan "pending" indefinidamente

**Solución:**

```bash
# 1. Revisar logs del worker
docker-compose logs worker

# 2. Revisar estado en Redis
redis-cli
> KEYS celery*
> HGETALL celery-task-meta-<task_id>

# 3. Limpiar tareas viejas
poetry run python manage.py retry_failed_jobs --hours 1

# 4. Reiniciar worker
docker-compose restart worker
```text

---

## 📈 Escalado

### Aumentar Concurrencia de Workers

**Docker Compose:**
```yaml
worker:
  command: celery -A project worker -Q default,documents --concurrency=8
  # Aumentar concurrency de 4 a 8
```text

**Local:**
```bash
poetry run celery -A project worker -Q default,documents --concurrency=8
```text

---

### Múltiples Workers Especializados

```bash
# Terminal 1: Worker para documentos
poetry run celery -A project worker -Q documents --concurrency=4 -n worker1@%h

# Terminal 2: Worker para tareas por defecto
poetry run celery -A project worker -Q default --concurrency=2 -n worker2@%h
```text

**En Docker Compose:**
```yaml
worker-docs:
  command: celery -A project worker -Q documents --concurrency=4 -n worker-docs@%h

worker-default:
  command: celery -A project worker -Q default --concurrency=2 -n worker-default@%h
```text

---

### Optimizar Redis

**Configuración en Redis:**
```text
maxmemory 512mb
maxmemory-policy allkeys-lru
```text

**En docker-compose.yml:**
```yaml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```text

---

### Usar Gunicorn en desarrollo

```bash
# Con múltiples workers
poetry run gunicorn project.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --access-logfile - \
  --error-logfile -
```text

---

## 🎨 Personalizar Plantillas

### Crear nueva plantilla

**1. Crear archivo `templates_doc/reporte.html.j2`:**

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial; }
    h1 { color: #333; }
  </style>
</head>
<body>
  <h1>{{ titulo }}</h1>
  <p>{{ contenido }}</p>
  <p>Generado: {% now "d/m/Y H:i" %}</p>
</body>
</html>
```text

**2. Registrar en `settings.py`:**

```python
SUPPORTED_DOCUMENT_TYPES = {
    'contract': 'contract.html.j2',
    'invoice': 'invoice.html.j2',
    'certificate': 'certificate.html.j2',
    'reporte': 'reporte.html.j2',  # NUEVA
}
```text

**3. Usar:**

```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=reporte" \
  -F "file=@mi_reporte.json"
```text

---

## 📝 Notas Importantes

### Versiones de Imágenes Docker

Para fijar versiones específicas:

```yaml
# En docker-compose.yml
db:
  image: bitnami/postgresql:17.1  # Versión específica
redis:
  image: bitnami/redis:7.2        # Versión específica
```text

---

### Variables de Entorno Críticas

```bash
# .env
SECRET_KEY=tu-clave-secreta-de-produccion
DEBUG=False  # SIEMPRE False en producción
ALLOWED_HOSTS=tu-dominio.com
DATABASE_PASSWORD=contraseña-fuerte
DJANGO_SUPERUSER_PASSWORD=contraseña-fuerte
```text

---

### Backup de Base de Datos

```bash
# Exportar PostgreSQL
docker-compose exec db pg_dump -U djangouser djangodb > backup.sql

# Restaurar
docker-compose exec db psql -U djangouser djangodb < backup.sql
```text

---

### Limpieza de Datos

```bash
# Eliminar documentos generados antiguos
find generated/ -mtime +30 -delete

# Limpiar uploads
find uploads/ -mtime +7 -delete

# Vaciar caché Redis
redis-cli FLUSHALL
```text

---

## 📞 Soporte

Para reportar problemas o sugerencias:

1. Revisar los logs: `docker-compose logs -f`
2. Verificar estado de servicios: `docker-compose ps`
3. Probar con ejemplos: `example_contract.json`, etc.
4. Revisar la sección [Troubleshooting](#troubleshooting)

---

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente.

---

**Última actualización:** Enero 2025  
**Versión de Django:** 6.0+  
**Versión de Celery:** 5.6+  
**Versión de Python:** 3.12+
