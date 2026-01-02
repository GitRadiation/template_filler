# 📂 Complete Project Structure

Complete map of Template Filler project with descriptions of each file.

---

## Root Directory

```text
template_filler/
├── README.md                    # Complete main documentation
├── QUICKSTART.md               # Quick start guide
├── TESTING.md                  # Comprehensive testing guide
├── .env.example                # Environment variables example
├── .gitignore                  # Files to ignore in Git
├── Dockerfile                  # Docker image for application
├── docker-compose.yml          # Docker services orchestration
├── manage.py                   # Django CLI
├── wsgi.py                     # WSGI entry point
├── pyproject.toml              # Poetry dependencies
├── poetry.lock                 # Exact version lock
├── .editorconfig               # Editor configuration
```

---

## `project/` Directory (Django Configuration)

```text
project/
├── __init__.py                 # Initializes Celery when Django loads
├── settings.py                 # Complete configuration (CRITICAL)
│   ├── Base dir and paths
│   ├── SECRET_KEY, DEBUG, ALLOWED_HOSTS
│   ├── Installed applications
│   ├── Middleware
│   ├── DATABASES (PostgreSQL)
│   ├── TEMPLATES
│   ├── Password validators
│   ├── Internationalization
│   ├── Static files and Media
│   ├── CELERY_* (Complete Celery configuration)
│   ├── CORS_ALLOWED_ORIGINS
│   └── LOGGING
├── urls.py                     # Project root routes
│   ├── /admin/ → Django Admin
│   └── /api/docs/ → docs app routes
├── wsgi.py                     # Entry point for Gunicorn/production
├── asgi.py                     # Entry point for Daphne/WebSockets
└── celery.py                   # Celery configuration (CRITICAL)
    ├── Initializes Celery app
    ├── Loads config from settings
    ├── Auto-discovers tasks
    └── Defines debug task
```

---

## `docs/` Directory (Main Application)

### Models

```text
docs/models.py
├── DocumentJob (Main model)
│   ├── id: UUIDField (primary key)
│   ├── celery_task_id: CharField (Celery tracking)
│   ├── template_name: ChoiceField (contract/invoice/certificate)
│   ├── input_file: FileField (uploaded JSON)
│   ├── output_file: FileField (generated PDF)
│   ├── status: ChoiceField (pending/running/completed/failed)
│   ├── error_message: TextField
│   ├── created_at, updated_at, started_at, completed_at: DateTimeField
│   ├── input_data: JSONField (template data)
│   └── Helper methods (is_completed, mark_running, etc)
```

### Views

```text
docs/views.py
├── UploadView(View)
│   ├── GET: Renders upload form upload.html
│   └── POST: Processes JSON file and creates DocumentJob
├── StatusView(View)
│   └── GET: Returns job status as JSON
├── DownloadView(View)
│   └── GET: Downloads generated PDF file
└── ListJobsView(View)
    └── GET: Lists jobs with filters (for debugging)
```

### Celery Tasks

```text
docs/tasks.py
├── generate_pdf_task(job_id)
│   ├── Gets job from DB
│   ├── Renders Jinja2 template
│   ├── Converts HTML → PDF with WeasyPrint
│   └── Saves to output_file
├── generate_docx_task(job_id)
│   ├── Similar but generates DOCX
├── generate_json_task(job_id)
│   ├── Generates JSON with processed data
├── _render_template(template_name, context)
├── _html_to_pdf(html_content)
└── _process_data(data)
```

### Services (Business Logic)

```text
docs/services.py
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
docs/urls.py
├── /upload/               → UploadView (GET/POST)
├── /status/<uuid>/        → StatusView (GET)
├── /download/<uuid>/      → DownloadView (GET)
└── /jobs/                 → ListJobsView (GET, for debugging)
```

### Admin

```text
docs/admin.py
├── DocumentJobAdmin
│   ├── list_display: ID, type, status, date, download button
│   ├── list_filter: status, type, date
│   ├── search_fields: ID, type, error message
│   ├── readonly_fields: (read-only fields)
│   ├── fieldsets: Visual organization
│   ├── actions: retry_failed_jobs, mark_as_pending
│   └── Custom colors and badges
```

### HTML Templates

```text
docs/templates/docs/upload.html
├── <header> with title and description
├── <form id="uploadForm">
│   ├── select#templateSelect (template dropdown)
│   ├── .drag-drop-zone (drag zone)
│   ├── input#hiddenFileInput (hidden file input)
│   └── buttons (submit and reset)
├── #statusContainer (status and result display)
├── <style> complete integrated CSS
└── <script> vanilla JavaScript (no external libraries)
    ├── Drag & drop handlers
    ├── Form submission
    ├── Status polling
    └── Download management
```

### Migrations

```text
docs/migrations/
├── __init__.py
└── 0001_initial.py          # Auto-created with makemigrations
    └── Creates docs_documentjob table
```

### Management Commands

```text
docs/management/commands/retry_failed_jobs.py
├── Command: python manage.py retry_failed_jobs
├── Options:
│   ├── --limit (default: 10)
│   └── --hours (default: 24)
└── Retry failed jobs by resetting to "pending"
```

### Other

```text
docs/
├── __init__.py              # Package marker
├── apps.py                  # App configuration
└── admin.py                 # Admin registration
```

---

## `templates_doc/` Directory (Jinja2 Templates)

### File Structure

```text
templates_doc/
├── contract.html.j2
│   ├── HTML5 with DOCTYPE
│   ├── <head> with complete <style> CSS
│   ├── Sections:
│   │   ├── Header (title, date)
│   │   ├── Contracting parties
│   │   ├── Contract object
│   │   ├── Duration
│   │   ├── Economic conditions (table)
│   │   ├── Terms and conditions
│   │   └── Signatures
│   ├── Jinja2 variables:
│   │   ├── {{ contracting_party_name }}
│   │   ├── {{ contractor_name }}
│   │   ├── {{ services }} (loop for)
│   │   ├── {{ total_amount }}
│   │   └── ... 15+ variables
│   └── {% if %}, {% for %} for logic
│
├── invoice.html.j2
│   ├── Structure:
│   │   ├── Header (company, number, date)
│   │   ├── Billing information
│   │   ├── Payment information (bank, IBAN)
│   │   ├── Items table (quantity, price, subtotal)
│   │   ├── Totals (subtotal, discount, VAT, total)
│   │   └── Notes
│   ├── Variables: company_*, customer_*, items[], totals, etc
│   └── Professional styles with corporate colors
│
└── certificate.html.j2
    ├── Elegant certificate-style design
    ├── Elements:
    │   ├── Header with institution
    │   ├── "CERTIFICATE" title
    │   ├── Recipient
    │   ├── Achievement/certification text
    │   ├── Details (course, duration, date)
    │   ├── Authorizer signatures
    │   └── Seal/Validation
    ├── Variables: recipient_name, achievement_text, signatures, etc
    └── Premium styles (gold, gradients, serif fonts)
```

### How Templates Work

1. User uploads JSON with data
2. `_render_template()` loads `.j2` file
3. Jinja2 renders with `template.render(**context)`
4. Resulting HTML is converted to PDF
5. PDF is saved in DB

### Usage Example

```python
# Input JSON data
data = {
    "contracting_party_name": "ABC Inc",
    "contractor_name": "John Doe",
    ...
}

# Jinja2 renders
template.render(**data)
# Generates HTML with actual values
```

---

## Data Directories (Generated at Runtime)

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
├── (user multimedia files)

staticfiles/
├── admin/
│   ├── css/
│   ├── js/
│   └── img/
└── (application CSS and JS)
```

---

## Example Data Files

```text
example_contract.json
├── Complete data to generate contract
├── Includes:
│   ├── Party data
│   ├── Services with prices
│   ├── Terms and conditions
│   └── All required information
└── ~70 lines of well-formed JSON

example_invoice.json
├── Data for invoice
├── Includes:
│   ├── Company and customer information
│   ├── Product/service details
│   ├── Calculations (subtotal, discounts, taxes)
│   └── Payment information
└── ~60 lines

example_certificate.json
├── Data for certificate
├── Includes:
│   ├── Beneficiary name
│   ├── Achievement and description
│   ├── Course/program
│   ├── Authorized signatures
│   └── Dates
└── ~20 lines (more compact)
```

---

## Docker Configuration Files

```text
docker-compose.yml (complete orchestration)
├── services:
│   ├── db (PostgreSQL 17)
│   │   ├── Image: bitnami/postgresql:17
│   │   ├── Persistent volumes
│   │   ├── Health checks
│   │   └── Environment variables
│   ├── redis (Redis 7)
│   │   ├── Image: bitnami/redis:7
│   │   ├── Ports
│   │   └── Health checks
│   ├── web (Django + Gunicorn)
│   │   ├── Build: Dockerfile
│   │   ├── Command: Migrations + Collectstatic + Gunicorn
│   │   ├── Dependencies with health checks
│   │   ├── Volumes: code, generated, uploads, media, static
│   │   └── Port 8000
│   ├── worker (Celery Worker)
│   │   ├── 4 worker concurrency
│   │   ├── Queues: default, documents
│   │   └── Automatic retries
│   └── flower (Monitor Celery)
│       ├── Port 5555
│       └── Real-time dashboard
└── volumes: Named persistent volumes

Dockerfile
├── FROM python:3.12-slim
├── Install system dependencies (WeasyPrint)
├── Install Poetry
├── Install Python dependencies
├── Create directories
├── Expose port 8000
├── Health check
└── CMD: Gunicorn
```

---

## Project Configuration Files

```text
pyproject.toml (dependency management)
├── [project]
│   ├── name = "template-filler"
│   ├── version = "0.1.0"
│   └── dependencies = [...]
├── django (6.0+)
├── celery (5.6+)
├── weasyprint (for PDF)
├── python-decouple (environment variables)
├── psycopg2-binary (PostgreSQL)
├── gunicorn (WSGI server)
├── docxtpl (DOCX)
├── django-cors-headers
├── pillow (images)
├── jinja2 (templates)
└── [build-system]

.env.example (variables template)
├── DEBUG, SECRET_KEY
├── DATABASE_* (PostgreSQL)
├── CELERY_* (Redis, queues)
├── DJANGO_SUPERUSER_*
└── EMAIL_* (optional)

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

## File Flow Diagram

```text
User loads JSON
        ↓
    upload.html (frontend)
        ↓
    UploadView.post() (views.py)
        ↓
    DocumentService.create_job() (services.py)
        ↓
    DocumentJob saved in DB (models.py)
        ↓
    DocumentService.send_to_celery() (services.py)
        ↓
    Task in Redis (broker)
        ↓
    Worker receives task (Celery worker)
        ↓
    generate_pdf_task() (tasks.py)
        ├─ Load template (templates_doc/contract.html.j2)
        ├─ Render with Jinja2
        ├─ Convert to PDF with WeasyPrint
        └─ Save to output_file
        ↓
    DocumentJob.status = "completed"
        ↓
    User checks StatusView
        ↓
    User downloads in DownloadView
        ↓
    PDF served from media/generated/
```

---

## Quick References

### To Add New Template

1. Create `templates_doc/new_template.html.j2`
2. Add to `settings.py` SUPPORTED_DOCUMENT_TYPES
3. Create JSON example `example_new_template.json`
4. Already available in API

### To Create New Task

1. Create function in `docs/tasks.py`
2. Decorate with `@shared_task`
3. Register route in `settings.py` CELERY_TASK_ROUTES (optional)
4. Call from service with `task.apply_async()`

### To Customize Admin

Edit `docs/admin.py`:

- `list_display` for columns
- `list_filter` for filters
- `search_fields` for search
- `actions` for batch actions

---

**Last updated:** January 2025  
**Version:** 1.0.0
