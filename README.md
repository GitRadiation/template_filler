# 📄 Template Filler - Complete Document Generator

Complete system for generating professional documents (PDF, DOCX, JSON) using Jinja2 templates, Django, Celery and Redis. Includes drag-and-drop interface, asynchronous processing and real-time monitoring.

---

## 📦 Requirements

### Local

- Python 3.12+
- Poetry
- PostgreSQL 15+
- Redis 7+
- LibreOffice/WeasyPrint dependencies

### Docker

- Docker
- Podman-compose (or docker-compose)

---

## 🚀 Local Installation

### 1. Clone and configure

```bash
cd /home/user/UNIVERSIDAD/template_filler
```

### 2. Create `.env` file (Optional, for default values)

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
```

### 3. Install dependencies with Poetry

```bash
poetry install
```

### 4. Configure PostgreSQL

```bash
# Create database
createdb -U postgres djangodb

# Create user
psql -U postgres -d djangodb -c "CREATE USER djangouser WITH PASSWORD 'secretpassword';"

# Grant permissions
psql -U postgres -d djangodb -c "GRANT ALL PRIVILEGES ON DATABASE djangodb TO djangouser;"
```

### 5. Start Redis

```bash
redis-server
# Or in another terminal:
# redis-cli
```

### 6. Django Migrations

```bash
poetry run python manage.py migrate
```

### 7. Create superuser

```bash
poetry run python manage.py createsuperuser
```

### 8. Create necessary directories

```bash
mkdir -p generated uploads media staticfiles
```

### 9. Run Django server

```bash
poetry run python manage.py runserver
# Accessible at: http://localhost:8000
```

### 10. Run Celery worker (in another terminal)

```bash
poetry run celery -A project worker --loglevel=info
```

### 11. (Optional) Run Flower for monitoring

```bash
poetry run celery -A project flower
# Accessible at: http://localhost:5555
```

---

## 🐳 Docker Installation

### 1. Build images

```bash
docker-compose build
```

### 2. Start services

```bash
docker-compose up -d
```

This will start:

- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Django Web** on port 8000
- **Celery Worker** processing tasks
- **Flower** (monitoring) on port 5555

### 3. Verify it's working

```bash
# View logs
docker-compose logs -f web

# Check service health
docker-compose ps

# Access the application
curl http://localhost:8000
```

### 4. Create superuser (if not created automatically)

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Stop services

```bash
docker-compose down

# To delete volumes (WARNING - deletes data):
docker-compose down -v
```

---

## 📁 Project Structure

```text
template_filler/
├── project/                    # Django configuration
│   ├── __init__.py
│   ├── settings.py             # Complete configuration (includes Celery)
│   ├── urls.py                 # Root URLs
│   ├── wsgi.py                 # WSGI entry point
│   ├── asgi.py                 # ASGI entry point
│   └── celery.py               # Celery configuration
│
├── docs/                 # Main application
│   ├── models.py               # DocumentJob model
│   ├── views.py                # UploadView, StatusView, DownloadView
│   ├── urls.py                 # Routes /upload/, /status/, /download/
│   ├── services.py             # DocumentService (business logic)
│   ├── tasks.py                # Celery tasks (generate_pdf, generate_docx, etc)
│   ├── admin.py                # Django Admin
│   ├── apps.py                 # App configuration
│   ├── templates/
│   │   └── docs/
│   │       └── upload.html     # Drag-and-drop interface
│   ├── migrations/
│   │   └── __init__.py
│   └── management/
│       └── commands/
│           └── retry_failed_jobs.py  # Command to retry jobs
│
├── templates_doc/              # Jinja2 templates
│   ├── contract.html.j2        # Contract template
│   ├── invoice.html.j2         # Invoice template
│   └── certificate.html.j2     # Certificate template
│
├── generated/                  # Generated documents (PDFs)
├── uploads/                    # User uploaded files
├── media/                      # Media files
├── staticfiles/                # Static CSS, JS
│
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Docker image
├── manage.py                   # Django entry point
├── pyproject.toml              # Poetry dependencies
├── example_contract.json       # Example: contract input
├── example_invoice.json        # Example: invoice input
├── example_certificate.json    # Example: certificate input
└── README.md                   # This file
```

---

## ⚙️ Celery Configuration

### Broker and Backend

**Broker** (message transport): Redis

```text
redis://localhost:6379/0
```

**Backend** (results storage): Redis

```text
redis://localhost:6379/1
```

### Configured Queues

```python
CELERY_QUEUES = {
    'default': { ... },      # Generic tasks
    'documents': { ... },    # Document tasks
}
```

### Task Routes

```python
CELERY_TASK_ROUTES = {
    'docs.tasks.generate_pdf_task': {'queue': 'documents'},
    'docs.tasks.generate_docx_task': {'queue': 'documents'},
    'docs.tasks.generate_json_task': {'queue': 'documents'},
}
```

### Retry Configuration

```python
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # seconds
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
```

### Run Worker

**Local with Poetry:**

```bash
poetry run celery -A project worker --loglevel=info
```

**Local with specific workers:**

```bash
# Worker for 'documents' queue
poetry run celery -A project worker -Q documents --loglevel=info

# Multiple workers
poetry run celery -A project worker -Q default,documents --concurrency=4
```

**Docker:**

```bash
docker-compose up worker
```

---

## 🔌 API Endpoints

### 1. Subir Documento (GET/POST)

```text
GET /api/docs/upload/
POST /api/docs/upload/
```text

**Successful POST response (201):**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Document generation in progress"
}
```

**POST Parameters:**

- `template_name` (required): 'contract' | 'invoice' | 'certificate'
- `file` (required): JSON file with data

**Example with cURL:**

```bash
curl -X POST http://localhost:8000/api/docs/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"
```

---

### 2. Check Status

```text
GET /api/docs/status/<job_id>/
```

**Response:**

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
```

**Possible states:**

- `pending`: Waiting for processing
- `running`: In progress
- `completed`: Successfully completed
- `failed`: Error during generation

**Example:**

```bash
curl http://localhost:8000/api/docs/status/550e8400-e29b-41d4-a716-446655440000/
```

---

### 3. Download Document

```text
GET /api/docs/download/<job_id>/
```

**Response:** PDF file downloaded

**Example:**

```bash
curl -o documento.pdf http://localhost:8000/api/docs/download/550e8400-e29b-41d4-a716-446655440000/
```

---

### 4. List Jobs (Debugging)

```text
GET /api/docs/jobs/
```

**Optional parameters:**

- `status`: 'pending' | 'running' | 'completed' | 'failed'
- `template`: 'contract' | 'invoice' | 'certificate'
- `limit`: Max number (default: 50)

**Example:**

```bash
curl "http://localhost:8000/api/docs/jobs/?status=completed&limit=10"
```

---

## 📋 Usage Examples

### Example 1: Generate Contract

**1. Prepare JSON data:**

```bash
cat > contract_data.json << 'EOF'
{
  "contracting_party_name": "ABC Company Inc",
  "contracting_party_id": "12.345.678-9",
  "contracting_party_address": "Main Street 123, Santiago",
  "contractor_name": "John Doe",
  "contractor_id": "98.765.432-1",
  "contractor_address": "Secondary Avenue 456, Santiago",
  "contract_object": "Business consulting services",
  "start_date": "01/01/2025",
  "end_date": "31/12/2025",
  "duration": "12 months",
  "services": [
    {
      "description": "Consulting Phase I",
      "unit_price": "5000000",
      "quantity": 1,
      "total": "5000000"
    }
  ],
  "total_amount": "5000000",
  "payment_method": "Bank transfer",
  "terms_and_conditions": "Both parties agree..."
}
EOF
```

**2. Send to server:**

```bash
curl -X POST http://localhost:8000/api/docs/upload/ \
  -F "template_name=contract" \
  -F "file=@contract_data.json"
```

**3. Response:**

```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

**4. Check status:**

```bash
curl http://localhost:8000/api/docs/status/550e8400-e29b-41d4-a716-446655440000/
```

**5. Download when completed:**

```bash
curl -o contract.pdf \
  http://localhost:8000/api/docs/download/550e8400-e29b-41d4-a716-446655440000/
```

---

### Example 2: Use Web Interface (Drag & Drop)

**1. Open in browser:**

```text
http://localhost:8000/api/docs/upload/
```

**2. Steps:**

- Select template type (Contract, Invoice, Certificate)
- Drag JSON file or click to select
- Click "Generate Document"
- Wait for it to complete
- Download PDF

---

### Example 3: Generate Invoice

```bash
# 1. With file
curl -X POST http://localhost:8000/api/docs/upload/ \
  -F "template_name=invoice" \
  -F "file=@example_invoice.json"

# 2. With direct JSON (POST form data)
curl -X POST http://localhost:8000/api/docs/upload/ \
  -F "template_name=invoice" \
  -F "data={\"company_name\": \"Tech Solutions Inc\", ...}"
```

---

### Example 4: Retry Failed Jobs

```bash
# Retry last 10 failed jobs
poetry run python manage.py retry_failed_jobs --limit 10

# Retry jobs from last 24 hours
poetry run python manage.py retry_failed_jobs --hours 24
```

---

### Example 5: Admin Panel

**1. Access:**

```text
http://localhost:8000/admin/
```

**2. Credentials (default with Docker):**

- Username: `admin`
- Password: `admin123`

**3. Functions:**

- View all document jobs
- Filter by state, template, date
- Retry failed jobs (action button)
- Mark as pending
- Download generated documents

---

## 📊 Monitoring with Flower

**Access Flower:**

```text
http://localhost:5555
```

**Features:**

- Real-time worker monitoring
- Task history
- Per-second statistics
- Cancel tasks
- Pool management
- Performance graphs

**Useful commands:**

```bash
# Start Flower (local)
poetry run celery -A project flower

# With custom port
poetry run celery -A project flower --port=5556

# With data persistence
poetry run celery -A project flower --persistent=True --db=flower.db
```

---

## 🔍 Troubleshooting

### Problem: "Could not resolve import 'decouple'"

**Solution:**

```bash
poetry install
# Or install manually:
pip install python-decouple
```

---

### Problem: Celery not processing tasks

**Verify:**

```bash
# 1. Redis is running
redis-cli ping
# Should return: PONG

# 2. Worker is running
poetry run celery -A project worker --loglevel=debug

# 3. Queue is configured correctly
# Check in project/settings.py: CELERY_BROKER_URL
```

---

### Problem: Database does not exist

**Solution:**

```bash
# PostgreSQL
createdb -U postgres djangodb
psql -U postgres -d djangodb -c "CREATE USER djangouser WITH PASSWORD 'secretpassword';"

# Then migrate
poetry run python manage.py migrate
```

---

### Problem: Port 8000 already in use

**Solution:**

```bash
# Use different port
poetry run python manage.py runserver 0.0.0.0:8080

# Or free port
lsof -i :8000
kill -9 <PID>
```

---

### Problem: WeasyPrint doesn't generate PDF

**Verify dependencies:**

```bash
# On Ubuntu/Debian
sudo apt-get install libffi-dev libcairo2-dev libpango1.0-dev libpangoft2-1.0-0

# On macOS
brew install libffi cairo pango gdk-pixbuf

# Reinstall WeasyPrint
pip install --force-reinstall WeasyPrint
```

---

### Problem: Tasks stuck in "pending" indefinitely

**Solution:**

```bash
# 1. Check worker logs
docker-compose logs worker

# 2. Check status in Redis
redis-cli
> KEYS celery*
> HGETALL celery-task-meta-<task_id>

# 3. Clean old tasks
poetry run python manage.py retry_failed_jobs --hours 1

# 4. Restart worker
docker-compose restart worker
```

---

## 📈 Scaling

### Increase Worker Concurrency

**Docker Compose:**

```yaml
worker:
  command: celery -A project worker -Q default,documents --concurrency=8
  # Increase concurrency from 4 to 8
```

**Local:**

```bash
poetry run celery -A project worker -Q default,documents --concurrency=8
```

---

### Multiple Specialized Workers

```bash
# Terminal 1: Worker for documents
poetry run celery -A project worker -Q documents --concurrency=4 -n worker1@%h

# Terminal 2: Worker for default tasks
poetry run celery -A project worker -Q default --concurrency=2 -n worker2@%h
```

**In Docker Compose:**

```yaml
worker-docs:
  command: celery -A project worker -Q documents --concurrency=4 -n worker-docs@%h

worker-default:
  command: celery -A project worker -Q default --concurrency=2 -n worker-default@%h
```

---

### Optimize Redis

**Redis Configuration:**

```text
maxmemory 512mb
maxmemory-policy allkeys-lru
```

**In docker-compose.yml:**

```yaml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

---

### Use Gunicorn in development

```bash
# With multiple workers
poetry run gunicorn project.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --worker-class gthread \
  --access-logfile - \
  --error-logfile -
```

---

## 🎨 Customize Templates

### Create new template

**1. Create file `templates_doc/report.html.j2`:**

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
  <h1>{{ title }}</h1>
  <p>{{ content }}</p>
  <p>Generated: {% now "d/m/Y H:i" %}</p>
</body>
</html>
```

**2. Register in `settings.py`:**

```python
SUPPORTED_DOCUMENT_TYPES = {
    'contract': 'contract.html.j2',
    'invoice': 'invoice.html.j2',
    'certificate': 'certificate.html.j2',
    'report': 'report.html.j2',  # NEW
}
```

**3. Use:**

```bash
curl -X POST http://localhost:8000/api/docs/upload/ \
  -F "template_name=report" \
  -F "file=@my_report.json"
```

---

## 📝 Important Notes

### Docker Image Versions

To pin specific versions:

```yaml
# In docker-compose.yml
db:
  image: bitnami/postgresql:17.1  # Specific version
redis:
  image: bitnami/redis:7.2        # Specific version
```

---

### Critical Environment Variables

```bash
# .env
SECRET_KEY=your-production-secret-key
DEBUG=False  # ALWAYS False in production
ALLOWED_HOSTS=your-domain.com
DATABASE_PASSWORD=strong-password
DJANGO_SUPERUSER_PASSWORD=strong-password
```

---

### Database Backup

```bash
# Export PostgreSQL
docker-compose exec db pg_dump -U djangouser djangodb > backup.sql

# Restore
docker-compose exec db psql -U djangouser djangodb < backup.sql
```

---

### Data Cleanup

```bash
# Delete old generated documents
find generated/ -mtime +30 -delete

# Clean uploads
find uploads/ -mtime +7 -delete

# Clear Redis cache
redis-cli FLUSHALL
```

---

## 📞 Support

To report issues or suggestions:

1. Check the logs: `docker-compose logs -f`
2. Verify service health: `docker-compose ps`
3. Test with examples: `example_contract.json`, etc.
4. Review the [Troubleshooting](#-troubleshooting) section

---

## 📄 License

This project is open source. Use it freely.

---

**Last updated:** January 2025  
**Django version:** 6.0+  
**Celery version:** 5.6+  
**Python version:** 3.12+
