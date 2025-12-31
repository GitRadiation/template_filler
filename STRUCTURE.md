# 📂 Estructura Completa del Proyecto

Mapa completo del proyecto Template Filler con descripciones de cada archivo.

---

## Directorio Raíz

```text
template_filler/
├── README.md                    # Documentación principal completa
├── QUICKSTART.md               # Guía rápida para empezar
├── TESTING.md                  # Guía exhaustiva de pruebas
├── ADVANCED.md                 # Configuraciones avanzadas
├── .env.example                # Variables de entorno ejemplo
├── .gitignore                  # Archivos a ignorar en Git
├── Dockerfile                  # Imagen Docker para la aplicación
├── docker-compose.yml          # Orquestación de servicios Docker
├── manage.py                   # CLI de Django
├── wsgi.py                     # Entry point WSGI
├── pyproject.toml              # Dependencias Poetry
├── poetry.lock                 # Lock de versiones exactas
├── .editorconfig               # Configuración del editor
```

---

## Directorio `project/` (Configuración Django)

```text
project/
├── __init__.py                 # Inicializa Celery al cargar Django
├── settings.py                 # Configuración completa (CRÍTICO)
│   ├── Base dir y paths
│   ├── SECRET_KEY, DEBUG, ALLOWED_HOSTS
│   ├── Aplicaciones instaladas
│   ├── Middleware
│   ├── DATABASES (PostgreSQL)
│   ├── TEMPLATES
│   ├── Password validators
│   ├── Internationalización
│   ├── Static files y Media
│   ├── CELERY_* (Configuración completa de Celery)
│   ├── CORS_ALLOWED_ORIGINS
│   └── LOGGING
├── urls.py                     # Rutas raíz del proyecto
│   ├── /admin/ → Django Admin
│   └── /api/documentos/ → Rutas de app documentos
├── wsgi.py                     # Entry point para Gunicorn/producción
├── asgi.py                     # Entry point para Daphne/WebSockets
└── celery.py                   # Configuración de Celery (CRÍTICO)
    ├── Inicializa app de Celery
    ├── Carga config desde settings
    ├── Auto-descubre tareas
    └── Define tarea de debug
```

---

## Directorio `documentos/` (Aplicación Principal)

### Modelos

```text
documentos/models.py
├── DocumentJob (Modelo principal)
│   ├── id: UUIDField (primary key)
│   ├── celery_task_id: CharField (tracking de Celery)
│   ├── template_name: ChoiceField (contract/invoice/certificate)
│   ├── input_file: FileField (JSON subido)
│   ├── output_file: FileField (PDF generado)
│   ├── status: ChoiceField (pending/running/completed/failed)
│   ├── error_message: TextField
│   ├── created_at, updated_at, started_at, completed_at: DateTimeField
│   ├── input_data: JSONField (datos para plantilla)
│   └── Métodos helper (is_completed, mark_running, etc)
```

### Vistas

```text
documentos/views.py
├── UploadView(View)
│   ├── GET: Renderiza formulario upload.html
│   └── POST: Procesa archivo JSON y crea DocumentJob
├── StatusView(View)
│   └── GET: Retorna estado del trabajo en JSON
├── DownloadView(View)
│   └── GET: Descarga archivo PDF generado
└── ListJobsView(View)
    └── GET: Lista trabajos con filtros (para debugging)
```

### Tareas Celery

```text
documentos/tasks.py
├── generate_pdf_task(job_id)
│   ├── Obtiene job de BD
│   ├── Renderiza plantilla Jinja2
│   ├── Convierte HTML → PDF con WeasyPrint
│   └── Guarda en output_file
├── generate_docx_task(job_id)
│   ├── Similar pero genera DOCX
├── generate_json_task(job_id)
│   ├── Genera JSON con datos procesados
├── _render_template(template_name, context)
├── _html_to_pdf(html_content)
└── _process_data(data)
```

### Servicios (Lógica de Negocio)

```text
documentos/services.py
├── DocumentService
│   ├── create_job(template_name, input_data, input_file)
│   ├── send_to_celery(job)
│   ├── get_job_status(job_id)
│   ├── save_output_file(job, output_content, file_name)
│   ├── get_job(job_id)
│   └── list_jobs(status, template_name, limit)
```

### URLs

```text
documentos/urls.py
├── /upload/               → UploadView (GET/POST)
├── /status/<uuid>/        → StatusView (GET)
├── /download/<uuid>/      → DownloadView (GET)
└── /jobs/                 → ListJobsView (GET, para debugging)
```

### Admin

```text
documentos/admin.py
├── DocumentJobAdmin
│   ├── list_display: ID, tipo, estado, fecha, botón descarga
│   ├── list_filter: estado, tipo, fecha
│   ├── search_fields: ID, tipo, mensaje error
│   ├── readonly_fields: (campos de solo lectura)
│   ├── fieldsets: Organización visual
│   ├── actions: retry_failed_jobs, mark_as_pending
│   └── Colores y badges personalizados
```

### Templates HTML

```text
documentos/templates/documentos/upload.html
├── <header> con título y descripción
├── <form id="uploadForm">
│   ├── select#templateSelect (dropdown de plantillas)
│   ├── .drag-drop-zone (zona de arrastrar)
│   ├── input#hiddenFileInput (file input oculto)
│   └── buttons (submit y reset)
├── #statusContainer (para mostrar estado y resultado)
├── <style> completo e integrado
└── <script> JavaScript vanilla (sin librerías externas)
    ├── Drag & drop handlers
    ├── Form submission
    ├── Polling del estado
    └── Download management
```

### Migrations

```text
documentos/migrations/
├── __init__.py
└── 0001_initial.py          # Se crea automáticamente con makemigrations
    └── Crea tabla documentos_documentjob
```

### Management Commands

```text
documentos/management/commands/retry_failed_jobs.py
├── Comando: python manage.py retry_failed_jobs
├── Opciones:
│   ├── --limit (default: 10)
│   └── --hours (default: 24)
└── Reintentar trabajos fallidos reseteando a "pending"
```

### Otros

```text
documentos/
├── __init__.py              # Marcador de paquete
├── apps.py                  # Configuración de app
└── admin.py                 # Registro en admin
```

---

## Directorio `templates_doc/` (Plantillas Jinja2)

### Estructura de Archivos

```text
templates_doc/
├── contract.html.j2
│   ├── HTML5 con DOCTYPE
│   ├── <head> con <style> CSS completo
│   ├── Secciones:
│   │   ├── Header (título, fecha)
│   │   ├── Partes contratantes
│   │   ├── Objeto del contrato
│   │   ├── Duración
│   │   ├── Condiciones económicas (tabla)
│   │   ├── Términos y condiciones
│   │   └── Firmas
│   ├── Variables Jinja2:
│   │   ├── {{ contracting_party_name }}
│   │   ├── {{ contractor_name }}
│   │   ├── {{ services }} (loop for)
│   │   ├── {{ total_amount }}
│   │   └── ... más de 15 variables
│   └── {% if %}, {% for %} para lógica
│
├── invoice.html.j2
│   ├── Estructura:
│   │   ├── Header (empresa, número, fecha)
│   │   ├── Información de facturación
│   │   ├── Información de pago (banco, IBAN)
│   │   ├── Tabla de items (cantidad, precio, subtotal)
│   │   ├── Totales (subtotal, descuento, IVA, total)
│   │   └── Notas
│   ├── Variables: company_*, customer_*, items[], totals, etc
│   └── Estilos profesionales con colores corporativos
│
└── certificate.html.j2
    ├── Diseño elegante tipo certificado
    ├── Elementos:
    │   ├── Header con institución
    │   ├── Título "CERTIFICADO"
    │   ├── Destinatario
    │   ├── Logro/Texto de certificación
    │   ├── Detalles (curso, duración, fecha)
    │   ├── Firmas de autorizantes
    │   └── Sello/Validación
    ├── Variables: recipient_name, achievement_text, signatures, etc
    └── Estilos premium (oro, gradientes, fuentes serif)
```

### Cómo Funcionan las Plantillas

1. Usuario sube JSON con datos
2. `_render_template()` carga archivo `.j2`
3. Jinja2 renderiza con `template.render(**context)`
4. HTML resultado se convierte a PDF
5. PDF se guarda en BD

### Ejemplo de Uso

```python
# Datos JSON de entrada
data = {
    "contracting_party_name": "ABC Inc",
    "contractor_name": "Juan Pérez",
    ...
}

# Jinja2 renderiza
template.render(**data)
# Genera HTML con valores reales
```

---

## Directorios de Datos (Generados en Runtime)

```text
generated/
├── 2025/
│   ├── 01/
│   │   ├── 15/
│   │   │   ├── 550e8400-e29b-41d4-a716-446655440000.pdf
│   │   │   ├── 550e8400-e29b-41d4-a716-446655440001.pdf
│   │   │   └── ...

uploads/
├── 2025/
│   ├── 01/
│   │   ├── 15/
│   │   │   ├── 550e8400-e29b-41d4-a716-446655440000_input.json
│   │   │   └── ...

media/
├── (archivos multimedia de usuarios)

staticfiles/
├── admin/
│   ├── css/
│   ├── js/
│   └── img/
└── (CSS y JS de aplicación)
```

---

## Ejemplos de Datos

```text
example_contract.json
├── Datos completos para generar contrato
├── Incluye:
│   ├── Datos de partes
│   ├── Servicios con precios
│   ├── Términos y condiciones
│   └── Toda la información requerida
└── ~70 líneas de JSON bien formado

example_invoice.json
├── Datos para factura
├── Incluye:
│   ├── Información de empresa y cliente
│   ├── Detalles de productos/servicios
│   ├── Cálculos (subtotal, descuentos, impuestos)
│   └── Información de pago
└── ~60 líneas

example_certificate.json
├── Datos para certificado
├── Incluye:
│   ├── Nombre del beneficiario
│   ├── Logro y descripción
│   ├── Curso/programa
│   ├── Firmas autorizadas
│   └── Fechas
└── ~20 líneas (más compacto)
```

---

## Archivos de Configuración Docker

```text
docker-compose.yml (orquestación completa)
├── services:
│   ├── db (PostgreSQL 17)
│   │   ├── Imagen: bitnami/postgresql:17
│   │   ├── Volúmenes persistentes
│   │   ├── Health checks
│   │   └── Variables de entorno
│   ├── redis (Redis 7)
│   │   ├── Imagen: bitnami/redis:7
│   │   ├── Puertos
│   │   └── Health checks
│   ├── web (Django + Gunicorn)
│   │   ├── Build: Dockerfile
│   │   ├── Comando: Migrations + Collectstatic + Gunicorn
│   │   ├── Dependencias con health checks
│   │   ├── Volúmenes: código, generated, uploads, media, static
│   │   └── Puerto 8000
│   ├── worker (Celery Worker)
│   │   ├── 4 workers de concurrencia
│   │   ├── Colas: default, documents
│   │   └── Reintentos automáticos
│   └── flower (Monitor Celery)
│       ├── Puerto 5555
│       └── Dashboard en tiempo real
└── volumes: Volúmenes nombrados persistentes

Dockerfile
├── FROM python:3.12-slim
├── Instalar dependencias del sistema (WeasyPrint)
├── Instalar Poetry
├── Instalar dependencias Python
├── Crear directorios
├── Exponer puerto 8000
├── Health check
└── CMD: Gunicorn
```

---

## Archivos de Configuración Project

```text
pyproject.toml (gestión de dependencias)
├── [project]
│   ├── name = "template-filler"
│   ├── version = "0.1.0"
│   └── dependencies = [...]
├── django (6.0+)
├── celery (5.6+)
├── weasyprint (para PDF)
├── python-decouple (variables de entorno)
├── psycopg2-binary (PostgreSQL)
├── gunicorn (servidor WSGI)
├── docxtpl (DOCX)
├── django-cors-headers
├── pillow (imágenes)
├── jinja2 (plantillas)
└── [build-system]

.env.example (template de variables)
├── DEBUG, SECRET_KEY
├── DATABASE_* (PostgreSQL)
├── CELERY_* (Redis, colas)
├── DJANGO_SUPERUSER_*
└── EMAIL_* (opcional)

.gitignore
├── __pycache__/
├── *.pyc
├── .env
├── media/
├── staticfiles/
├── generated/
├── uploads/
├── .venv/
├── .DS_Store
└── *.db
```

---

## Diagrama de Flujo de Archivos

```text
Usuario carga JSON
        ↓
    upload.html (frontend)
        ↓
    UploadView.post() (views.py)
        ↓
    DocumentService.create_job() (services.py)
        ↓
    DocumentJob guardado en BD (models.py)
        ↓
    DocumentService.send_to_celery() (services.py)
        ↓
    Tarea en Redis (broker)
        ↓
    Worker recibe tarea (Celery worker)
        ↓
    generate_pdf_task() (tasks.py)
        ├─ Carga template (templates_doc/contract.html.j2)
        ├─ Renderiza con Jinja2
        ├─ Convierte a PDF con WeasyPrint
        └─ Guarda en output_file
        ↓
    DocumentJob.status = "completed"
        ↓
    Usuario verifica StatusView
        ↓
    Usuario descarga en DownloadView
        ↓
    PDF servido desde media/generated/
```

---

## Referencias Rápidas

### Para Agregar Nueva Plantilla

1. Crear `templates_doc/new_template.html.j2`
2. Agregar en `settings.py` SUPPORTED_DOCUMENT_TYPES
3. Crear JSON ejemplo `example_new_template.json`
4. Ya está disponible en API

### Para Crear Nueva Tarea

1. Crear función en `documentos/tasks.py`
2. Decorar con `@shared_task`
3. Registrar ruta en `settings.py` CELERY_TASK_ROUTES (opcional)
4. Llamar desde servicio con `task.apply_async()`

### Para Personalizar Admin

Editar `documentos/admin.py`:

- `list_display` para columnas
- `list_filter` para filtros
- `search_fields` para búsqueda
- `actions` para acciones en lote

---

**Última actualización:** Enero 2025  
**Versión:** 1.0.0
