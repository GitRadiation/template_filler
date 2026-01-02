# 🧪 Testing Guide - Template Filler

This guide shows you how to test each component of the system step by step.

## ✅ Pre-Launch Checklist

Before launching to production, verify:

- [ ] PostgreSQL database is running
- [ ] Redis is running
- [ ] Environment variables are configured
- [ ] Django migrations are applied
- [ ] Superuser created
- [ ] Static files collected
- [ ] Output directories created
- [ ] Celery Worker is running
- [ ] Access to <http://localhost:8000>

---

## 🚀 Test 1: Basic Configuration

### Step 1: Verify Django installation

```bash
poetry run python manage.py --version
# Should show: Django 6.x.x
```

### Step 2: Run migrations

```bash
poetry run python manage.py migrate
# Should show:
# Operations to perform:
#   Apply all migrations: admin, auth, ...
# Running migrations:
#   Applying documentos.0001_initial... OK
```

### Step 3: Create superuser

```bash
poetry run python manage.py createsuperuser
# Enter:
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### Step 4: Verify database structure

```bash
poetry run python manage.py dbshell
# postgres=# \dt documentos_documentjob;
# postgres=# \q
```

---

## 🔄 Test 2: Queue System (Celery + Redis)

### Step 1: Verify Redis connection

```bash
redis-cli ping
# Should return: PONG

# Verify Redis structure
redis-cli
> INFO stats
> KEYS celery*
> QUIT
```

### Step 2: Start Celery Worker

```bash
poetry run celery -A project worker --loglevel=debug
```

**Expected output:**

```bash
 -------------- celery@user v5.6.0 (sun-hills)
--- ***** -----
-- ******* ----
- *** --- * ---
- ** ---------- [config]
- ** ----------
- ** ---------- app:         project:0x...
- ** ---------- transport:   redis://...
- *** --- * --- results:     redis://...
-- ******* ---- concurrency: 4 (prefork)
--- ***** ----- pool:        prefork
 -------------- [queues]
                .> documents          exchange=documents (durable) binding_key='documents'
                .> celery             exchange=celery (durable)   binding_key='celery'

[tasks]
  . documentos.tasks.debug_task
  . documentos.tasks.generate_docx_task
  . documentos.tasks.generate_json_task
  . documentos.tasks.generate_pdf_task
```

### Step 3: Test debug task (in another terminal)

```bash
poetry run python -c "
from project.celery import app
result = app.send_task('project.tasks.debug_task')
print('Task ID:', result.id)
"

# Verify in the worker that it processes the task
```

---

## 📄 Test 3: Document Generation

### Test 3a: Generate PDF (Contract)

### Terminal 1: Start Django

```bash
poetry run python manage.py runserver
```

### Terminal 2: Start Worker

```bash
poetry run celery -A project worker --loglevel=info
```

### Terminal 3: Send document

```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"
```

**Expected response:**

```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Document generation in progress"
}
```

### Check status

```bash
curl http://localhost:8000/api/documentos/status/550e8400-e29b-41d4-a716-446655440000/
```

### Wait and see status change

```json
{
  "status": "running",  // Later: "completed"
  ...
}
```

### Download when complete

```bash
curl -o contract.pdf \
  http://localhost:8000/api/documentos/download/550e8400-e29b-41d4-a716-446655440000/

# Verify file
file contract.pdf
# Should show: PDF document, version 1.4
```

---

### Test 3b: Generate Invoice

```bash
# Send
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=invoice" \
  -F "file=@example_invoice.json"

# Copy job_id and download when complete
curl -o invoice.pdf \
  http://localhost:8000/api/documentos/download/<job_id>/
```

---

### Test 3c: Generate Certificate

```bash
# Send
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=certificate" \
  -F "file=@example_certificate.json"

# Download
curl -o certificate.pdf \
  http://localhost:8000/api/documentos/download/<job_id>/
```

---

## 🖥️ Test 4: Drag & Drop Web Interface

### Step 1: Open browser

```text
http://localhost:8000/api/documentos/upload/
```

### Step 2: Test functionalities

### Test 1: Select template

- [ ] Select "Contract"
- [ ] Verify dropdown works

### Test 2: Drag & Drop

- [ ] Drag `example_contract.json` to zone
- [ ] Verify file name appears
- [ ] Verify validation error disappears

### Test 3: Click to select

- [ ] Click in zone
- [ ] Select `example_invoice.json`
- [ ] Verify name appears

### Test 4: Generate document

- [ ] Select "Invoice"
- [ ] Select `example_invoice.json`
- [ ] Click "Generate Document"
- [ ] Verify spinner appears
- [ ] Wait for completion
- [ ] Verify "Download" button appears

### Test 5: Download

- [ ] Click "Download Document"
- [ ] Verify PDF downloads

---

## 📊 Test 5: Monitoring with Flower

### Step 1: Start Flower

```bash
poetry run celery -A project flower
```

### Step 2: Access dashboard

```text
http://localhost:5555
```

### Step 3: Tests in Flower

### Test 1: See Workers

- [ ] Verify at least 1 worker appears
- [ ] See pool size (4 by default)
- [ ] See number of processes

### Test 2: Task Monitor

- [ ] Generate a document
- [ ] Verify task appears in "Tasks"
- [ ] See execution time
- [ ] See state (pending → received → started → succeeded)

### Test 3: Statistics

- [ ] Go to "Stats"
- [ ] See: pool.timeouts, total tasks, etc.

### Test 4: Graphs

- [ ] Generate multiple documents simultaneously
- [ ] See spike in "Tasks/sec"
- [ ] See workers online graph

---

## 🔐 Test 6: Admin Panel

### Step 1: Access Django Admin

```text
http://localhost:8000/admin/
```

**Credentials:**

- Username: `admin`
- Password: `admin123` (or what you configured)

### Step 2: Verify models

**Documents:**

- [ ] Click on "Document jobs"
- [ ] Should show list of DocumentJob
- [ ] Each item shows: ID, type, status, date

### Step 3: Test filters

- [ ] Filter by "Status: Completed"
- [ ] Filter by "Template type: Contract"
- [ ] Filter by "Created: Today"

### Step 4: Test search

- [ ] Search by job ID
- [ ] Search by template name

### Step 5: Download from Admin

- [ ] Click on a completed job
- [ ] Click "View/Download" link
- [ ] Verify PDF opens

### Step 6: Batch actions

- [ ] Select multiple failed jobs
- [ ] Click "Retry failed jobs"
- [ ] Verify they change to "Pending"

---

## ⚙️ Test 7: Error Handling

### Test 7a: Invalid JSON file

```bash
# Create malformed JSON file
echo '{"invalid json": }' > bad.json

# Send
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@bad.json"

# Expect error response
# {"error": "Invalid JSON file: ..."}
```

### Test 7b: Unsupported template

```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=invalid_type" \
  -F "file=@example_contract.json"

# Expect: "Unsupported template"
```

### Test 7c: Missing fields in JSON

```bash
# JSON without required fields
echo '{"field1": "value1"}' > minimal.json

curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@minimal.json"

# Should process (with empty fields in PDF)
# Or show error according to validation
```

### Test 7d: Job ID doesn't exist

```bash
curl http://localhost:8000/api/documentos/status/invalid-uuid/

# Expect: {"error": "Job not found"} (404)
```

---

## 🔄 Test 8: Retries and Recovery

### Step 1: Simulate failure

```bash
# Move template temporarily
mv templates_doc/contract.html.j2 templates_doc/contract.html.j2.bak

# Send document
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"

# Wait for it to fail (status: failed)
```

### Step 2: Restore and retry

```bash
# Restore template
mv templates_doc/contract.html.j2.bak templates_doc/contract.html.j2

# Retry failed jobs
poetry run python manage.py retry_failed_jobs --limit 5

# Verify it's now "pending"
curl http://localhost:8000/api/documentos/status/<job_id>/
```

### Step 3: Verify completion

```bash
# Wait and verify
curl http://localhost:8000/api/documentos/status/<job_id>/
# Should show: "status": "completed"
```

---

## 📦 Test 9: With Docker

### Step 1: Build images

```bash
docker-compose build
```

### Step 2: Start services

```bash
docker-compose up -d
```

### Step 3: Wait for startup

```bash
# View logs
docker-compose logs -f web

# Wait message: "Quit the server with CONTROL-C"
```

### Step 4: Verify health

```bash
docker-compose ps
# All should be "healthy" or "up"
```

### Step 5: Test endpoints

```bash
# Access admin
curl http://localhost:8000/admin/
# Should return HTML (200)

# Generate document
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"
```

### Step 6: View worker logs

```bash
docker-compose logs worker
# Should show task processing
```

### Step 7: Monitoring with Flower

```bash
# Access http://localhost:5555
curl http://localhost:5555
```

---

## 📈 Test 10: Load and Stress

### Test 10a: Generate multiple documents

```bash
#!/bin/bash
for i in {1..10}; do
  echo "Sending document $i..."
  curl -s -X POST http://localhost:8000/api/documentos/upload/ \
    -F "template_name=contract" \
    -F "file=@example_contract.json" | jq -r '.job_id'
done
```

### Test 10b: Monitor in Flower

- [ ] Open <http://localhost:5555>
- [ ] See spike in "Tasks/sec"
- [ ] See all workers processing
- [ ] See average execution time

### Test 10c: Verify DB

```bash
# Count documents in DB
poetry run python manage.py shell
>>> from documentos.models import DocumentJob
>>> DocumentJob.objects.count()
# Should be >= 10
```

---

## 🧹 Post-Test Cleanup

```bash
# Stop Docker
docker-compose down

# Delete generated files
rm -rf generated/*
rm -rf uploads/*

# Clean Redis
redis-cli FLUSHALL

# Clean DB (WARNING - deletes all)
poetry run python manage.py flush --no-input

# Reinitialize
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

---

## 📝 Features Tested Checklist

**Development:**

- [ ] Django runserver works
- [ ] Admin panel accessible
- [ ] DB migrated correctly

**Celery:**

- [ ] Redis works
- [ ] Worker starts without errors
- [ ] Debug task executes successfully

**API:**

- [ ] POST /upload/ with file
- [ ] GET /status/ returns status
- [ ] GET /download/ downloads PDF
- [ ] GET /jobs/ lists jobs

**Web:**

- [ ] Upload.html loads
- [ ] Drag & drop works
- [ ] Form validates inputs
- [ ] Spinner shows during generation
- [ ] Download button appears when complete

**Documents:**

- [ ] PDF generates correctly
- [ ] Jinja2 template renders data
- [ ] File saves to disk

**Admin:**

- [ ] Login works
- [ ] List jobs
- [ ] Filter by status
- [ ] Search by ID
- [ ] Download PDF from admin
- [ ] Retry failed jobs

**Monitoring:**

- [ ] Flower shows workers
- [ ] Flower shows tasks
- [ ] Flower shows statistics
- [ ] Graphs update

**Docker:**

- [ ] docker-compose up starts everything
- [ ] Services pass healthcheck
- [ ] API works from containers
- [ ] Volumes persist data

---

## 📊 Useful Testing Commands

```bash
# View logs in real time
docker-compose logs -f web
docker-compose logs -f worker
docker-compose logs -f

# Run command in container
docker-compose exec web python manage.py shell
docker-compose exec worker celery -A project inspect active

# Open bash in container
docker-compose exec web bash

# Inspect Celery tasks
celery -A project inspect active
celery -A project inspect stats
celery -A project inspect revoked

# List registered tasks
celery -A project inspect registered

# Monitor in real time
watch 'curl -s http://localhost:8000/api/documentos/jobs/ | jq'
```

---

**Last updated:** January 2025
