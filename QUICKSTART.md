# 🚀 Quick Start - Template Filler

Get started in 5 minutes.

---

## Option 1: With Docker (Recommended)

### 1. Start services

```bash
cd /home/user/UNIVERSIDAD/template_filler
docker-compose up -d
```

### 2. Wait for startup (30-60 seconds)

```bash
# View logs
docker-compose logs -f web
```

### 3. Access the application

```text
🌐 Upload: http://localhost:8000/api/documentos/upload/
🔐 Admin:  http://localhost:8000/admin/
📊 Flower: http://localhost:5555
```

**Admin Credentials:**

- Username: `admin`
- Password: `admin123`

### 4. Test document generation

```bash
# Generate contract
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"

# Response: {"success": true, "job_id": "..."}
```

---

## Option 2: Local (Without Docker)

### 1. Install dependencies

```bash
cd /home/user/UNIVERSIDAD/template_filler

# Ensure PostgreSQL and Redis are running
# (On Ubuntu: sudo service postgresql start, redis-server)

poetry install
```

### 2. Migrations

```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### 3. Start Django (Terminal 1)

```bash
poetry run python manage.py runserver
```

### 4. Start Celery Worker (Terminal 2)

```bash
poetry run celery -A project worker --loglevel=info
```

### 5. Start Flower (Terminal 3, optional)

```bash
poetry run celery -A project flower
```

### 6. Access

```text
🌐 Upload: http://localhost:8000/api/documentos/upload/
🔐 Admin:  http://localhost:8000/admin/
📊 Flower: http://localhost:5555
```

---

## Quick Test (30 seconds)

### Method 1: Browser

1. Go to `http://localhost:8000/api/documentos/upload/`
2. Select "Contract"
3. Drag `example_contract.json` to the zone
4. Click "Generate Document"
5. Wait and download the PDF

### Method 2: cURL

```bash
# 1. Send document
JOB_ID=$(curl -s -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json" | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# 2. Wait 5 seconds
sleep 5

# 3. Check status
curl http://localhost:8000/api/documentos/status/$JOB_ID/

# 4. Download (when status is "completed")
curl -o documento.pdf \
  http://localhost:8000/api/documentos/download/$JOB_ID/

# 5. Open PDF
open documento.pdf  # macOS
xdg-open documento.pdf  # Linux
start documento.pdf  # Windows
```

---

## 📁 Example Files

Inside the project you'll find:

- **`example_contract.json`** - Data to generate contract
- **`example_invoice.json`** - Data to generate invoice
- **`example_certificate.json`** - Data to generate certificate

Use them directly or create your own with the same structure.

---

## 🛑 Stop Services

### Docker

```bash
docker-compose down

# Stop and clean volumes (CAREFUL - deletes data)
docker-compose down -v
```

### Local

```bash
# Press Ctrl+C in each terminal
```

---

## 🐛 Something not working?

### Error: "Connection refused" on PostgreSQL

```bash
# Verify PostgreSQL is running
psql -U postgres -d postgres -c "SELECT 1"

# If not running (Linux)
sudo service postgresql start

# If not running (macOS with Homebrew)
brew services start postgresql
```

### Error: "Connection refused" on Redis

```bash
# Start Redis
redis-server

# Or in another terminal (if installed as service)
sudo service redis-server start
```

### Tasks are not processing

```bash
# 1. Verify Worker is running (should be in Terminal 2)
# 2. Check Worker logs for errors
# 3. In Flower: http://localhost:5555 (should show workers)
```

### Error: "No module named 'django'"

```bash
# Reinstall dependencies
poetry install
```

---

## 📊 Verify everything is working

```bash
# Django OK?
curl http://localhost:8000/admin/

# API OK?
curl http://localhost:8000/api/documentos/jobs/

# Flower OK?
curl http://localhost:5555

# Redis OK?
redis-cli ping  # Should return: PONG

# PostgreSQL OK?
psql -U djangouser -d djangodb -c "SELECT COUNT(*) FROM documentos_documentjob;"
```

---

## 🎯 Common use cases

### Generate only PDF contract

```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json" \
  | jq '.job_id' | xargs -I {} \
  curl http://localhost:8000/api/documentos/status/{} \
  | jq '.'
```

### List completed documents

```bash
curl "http://localhost:8000/api/documentos/jobs/?status=completed&limit=10"
```

### Retry failed documents

```bash
poetry run python manage.py retry_failed_jobs --limit 10
```

### Clean generated files

```bash
rm -rf generated/*
```

---

## 📚 Complete Documentation

For more information:

- **README.md** - Complete installation and usage guide
- **TESTING.md** - Detailed testing guide
- **ADVANCED.md** - Advanced configurations and optimizations

---

## 🎓 Learn the code

### Document generation flow

```text
1. User uploads JSON → UploadView (POST /api/documentos/upload/)
   ↓
2. DocumentService creates DocumentJob
   ↓
3. Sends task to Celery (tasks.generate_pdf_task)
   ↓
4. Celery Worker processes:
   - Loads Jinja2 template (templates_doc/*.html.j2)
   - Renders HTML with JSON data
   - Converts HTML → PDF with WeasyPrint
   - Saves PDF to DocumentJob.output_file
   ↓
5. User checks status → StatusView (GET /api/documentos/status/<job_id>/)
   ↓
6. Downloads PDF → DownloadView (GET /api/documentos/download/<job_id>/)
```

### Critical file structure

```text
project/
  ├─ celery.py         ← Celery initialization
  ├─ settings.py       ← Configuration (includes CELERY_*)
  └─ urls.py           ← Root routes

documentos/
  ├─ models.py         ← DocumentJob
  ├─ views.py          ← Upload, Status, Download
  ├─ tasks.py          ← generate_pdf_task, generate_docx_task, etc
  ├─ services.py       ← Logic: create job, send to Celery
  └─ urls.py           ← Routes /upload/, /status/, /download/

templates_doc/
  ├─ contract.html.j2
  ├─ invoice.html.j2
  └─ certificate.html.j2
```

---

## 💡 Tips

1. **Development**: Use `docker-compose` for identical production environment
2. **Debugging**: Open Flower (`http://localhost:5555`) to see task status
3. **Admin**: Use Django Admin (`http://localhost:8000/admin/`) to inspect DB
4. **Logs**: `docker-compose logs -f` to see everything in real time
5. **Restart**: `docker-compose restart` to restart services

---

## ⏱️ Expected time

| Task | Time |
| --- | --- |
| Clone repo | 1 min |
| Docker build | 3 min |
| Docker up | 1 min |
| First generation | 5 sec |

**Total: ~10 minutes** from scratch to first document generation.

---

## 🎉 Done

You have a complete document generation system with:

✅ Web interface with Drag & Drop  
✅ REST API  
✅ Asynchronous processing with Celery  
✅ Django admin panel  
✅ Real-time monitoring (Flower)  
✅ PDF, DOCX, JSON generation  
✅ PostgreSQL database  
✅ Redis cache  

**What's next?**

- Customize templates in `templates_doc/`
- Add new document types
- Integrate with your application
- Deploy to production with Docker

---

**Last updated:** January 2025  
**Version:** 1.0.0  
**License:** MIT
