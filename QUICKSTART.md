# 🚀 Quick Start - Template Filler

Comienza en 5 minutos.

---

## Opción 1: Con Docker (Recomendado)

### 1. Iniciar servicios

```bash
cd /home/user/UNIVERSIDAD/template_filler
docker-compose up -d
```

### 2. Esperar a que inicie (30-60 segundos)

```bash
# Ver logs
docker-compose logs -f web
```

### 3. Acceder a la aplicación

```text
🌐 Upload: http://localhost:8000/api/documentos/upload/
🔐 Admin:  http://localhost:8000/admin/
📊 Flower: http://localhost:5555
```

**Credenciales Admin:**

- Usuario: `admin`
- Contraseña: `admin123`

### 4. Probar generación de documentos

```bash
# Generar contrato
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"

# Respuesta: {"success": true, "job_id": "..."}
```

---

## Opción 2: Local (Sin Docker)

### 1. Instalar dependencias

```bash
cd /home/user/UNIVERSIDAD/template_filler

# Asegurar PostgreSQL y Redis corriendo
# (En Ubuntu: sudo service postgresql start, redis-server)

poetry install
```

### 2. Migraciones

```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

### 3. Iniciar Django (Terminal 1)

```bash
poetry run python manage.py runserver
```

### 4. Iniciar Worker Celery (Terminal 2)

```bash
poetry run celery -A project worker --loglevel=info
```

### 5. Iniciar Flower (Terminal 3, opcional)

```bash
poetry run celery -A project flower
```

### 6. Acceder

```text
🌐 Upload: http://localhost:8000/api/documentos/upload/
🔐 Admin:  http://localhost:8000/admin/
📊 Flower: http://localhost:5555
```

---

## Prueba Rápida (30 segundos)

### Método 1: Browser

1. Ir a `http://localhost:8000/api/documentos/upload/`
2. Seleccionar "Contrato"
3. Arrastra `example_contract.json` a la zona
4. Haz clic en "Generar Documento"
5. Espera y descarga el PDF

### Método 2: cURL

```bashbash
# 1. Enviar documento
JOB_ID=$(curl -s -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json" | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# 2. Esperar 5 segundos
sleep 5

# 3. Verificar estado
curl http://localhost:8000/api/documentos/status/$JOB_ID/

# 4. Descargar (cuando status sea "completed")
curl -o documento.pdf \
  http://localhost:8000/api/documentos/download/$JOB_ID/

# 5. Abrir PDF
open documento.pdf  # macOS
xdg-open documento.pdf  # Linux
start documento.pdf  # Windows
```

---

## 📁 Archivos de Ejemplo

Dentro del proyecto encontrarás:

- **`example_contract.json`** - Datos para generar contrato
- **`example_invoice.json`** - Datos para generar factura
- **`example_certificate.json`** - Datos para generar certificado

Úsalos directamente o crea los tuyos con la misma estructura.

---

## 🛑 Detener Servicios

### Docker

```bash
docker-compose down

# Detener y limpiar volúmenes (CUIDADO - borra datos)
docker-compose down -v
```

### Local

```bash
# Presionar Ctrl+C en cada terminal
```

---

## 🐛 Algo no funciona?

### Error: "Connection refused" en PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
psql -U postgres -d postgres -c "SELECT 1"

# Si no está corriendo (Linux)
sudo service postgresql start

# Si no está corriendo (macOS con Homebrew)
brew services start postgresql
```

### Error: "Connection refused" en Redis

```bash
# Iniciar Redis
redis-server

# O en otra terminal (si está instalado como servicio)
sudo service redis-server start
```

### Las tareas no se procesan

```bash
# 1. Verificar que Worker está corriendo (debe estar en Terminal 2)
# 2. Verificar logs del Worker para errores
# 3. En Flower: http://localhost:5555 (debe mostrar workers)
```

### Error: "No module named 'django'"

```bash
# Reinstalar dependencias
poetry install
```

---

## 📊 Verificar que todo está funcionando

```bash
# Django OK?
curl http://localhost:8000/admin/

# API OK?
curl http://localhost:8000/api/documentos/jobs/

# Flower OK?
curl http://localhost:5555

# Redis OK?
redis-cli ping  # Debe retornar: PONG

# PostgreSQL OK?
psql -U djangouser -d djangodb -c "SELECT COUNT(*) FROM documentos_documentjob;"
```

---

## 🎯 Casos de uso comunes

### Generar solo PDF de Contrato

```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json" \
  | jq '.job_id' | xargs -I {} \
  curl http://localhost:8000/api/documentos/status/{} \
  | jq '.'
```

### Listar documentos completados

```bash
curl "http://localhost:8000/api/documentos/jobs/?status=completed&limit=10"
```

### Reintentar documentos fallidos

```bash
poetry run python manage.py retry_failed_jobs --limit 10
```

### Limpiar archivos generados

```bash
rm -rf generated/*
```

---

## 📚 Documentación Completa

Para más información:

- **README.md** - Guía completa de instalación y uso
- **TESTING.md** - Guía de pruebas detallada
- **ADVANCED.md** - Configuraciones avanzadas y optimizaciones

---

## 🎓 Aprender el código

### Flujo de generación de documento

```text
1. Usuario sube JSON → UploadView (POST /api/documentos/upload/)
   ↓
2. DocumentService crea DocumentJob
   ↓
3. Envía tarea a Celery (tasks.generate_pdf_task)
   ↓
4. Worker Celery procesa:
   - Carga plantilla Jinja2 (templates_doc/*.html.j2)
   - Renderiza HTML con datos JSON
   - Convierte HTML → PDF con WeasyPrint
   - Guarda PDF en DocumentJob.output_file
   ↓
5. Usuario verifica estado → StatusView (GET /api/documentos/status/<job_id>/)
   ↓
6. Descarga PDF → DownloadView (GET /api/documentos/download/<job_id>/)
```

### Estructura de archivos crítica

```text
project/
  ├─ celery.py         ← Inicialización de Celery
  ├─ settings.py       ← Configuración (incluye CELERY_*)
  └─ urls.py           ← Rutas raíz

documentos/
  ├─ models.py         ← DocumentJob
  ├─ views.py          ← Upload, Status, Download
  ├─ tasks.py          ← generate_pdf_task, generate_docx_task, etc
  ├─ services.py       ← Lógica: crear job, enviar a Celery
  └─ urls.py           ← Rutas /upload/, /status/, /download/

templates_doc/
  ├─ contract.html.j2
  ├─ invoice.html.j2
  └─ certificate.html.j2
```

---

## 💡 Tips

1. **Desarrollo**: Usa `docker-compose` para ambiente idéntico a producción
2. **Debugging**: Abre Flower (`http://localhost:5555`) para ver estado de tareas
3. **Admin**: Usa Django Admin (`http://localhost:8000/admin/`) para inspeccionar BD
4. **Logs**: `docker-compose logs -f` para ver todo en tiempo real
5. **Reinicio**: `docker-compose restart` para reiniciar servicios

---

## ⏱️ Tiempo esperado

| Tarea | Tiempo |
|-------|--------|
| Clonar repo | 1 min |
| Docker build | 3 min |
| Docker up | 1 min |
| Primera generación | 5 seg |

**Total: ~10 minutos** desde cero a primera generación de documento.

---

## 🎉 Listo

Tienes un sistema completo de generación de documentos con:

✅ Interfaz web con Drag & Drop  
✅ API REST  
✅ Procesamiento asincrónico con Celery  
✅ Panel administrativo Django  
✅ Monitoreo en tiempo real (Flower)  
✅ Generación de PDF, DOCX, JSON  
✅ Base de datos PostgreSQL  
✅ Cache con Redis  

**¿Qué sigue?**

- Personaliza las plantillas en `templates_doc/`
- Agrega nuevos tipos de documentos
- Integra con tu aplicación
- Deploya en producción con Docker

---

**Última actualización:** Enero 2025  
**Versión:** 1.0.0  
**Licencia:** MIT
