# 🧪 Guía de Pruebas - Template Filler

Esta guía te muestra cómo probar cada componente del sistema step by step.

## ✅ Checklist Pre-Lanzamiento

Antes de lanzar a producción, verifica:

- [ ] Base de datos PostgreSQL está corriendo
- [ ] Redis está corriendo
- [ ] Variables de entorno están configuradas
- [ ] Migraciones Django están aplicadas
- [ ] Superusuario creado
- [ ] Static files recolectados
- [ ] Directorios de salida creados
- [ ] Worker Celery está ejecutándose
- [ ] Acceso a <http://localhost:8000>

---

## 🚀 Prueba 1: Configuración Básica

### Paso 1: Verificar instalación de Django

```bash
poetry run python manage.py --version
# Debe mostrar: Django 6.x.x
```

### Paso 2: Ejecutar migraciones

```bash
poetry run python manage.py migrate
# Debe mostrar:
# Operations to perform:
#   Apply all migrations: admin, auth, ...
# Running migrations:
#   Applying documentos.0001_initial... OK
```

### Paso 3: Crear superusuario

```bash
poetry run python manage.py createsuperuser
# Ingresa:
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### Paso 4: Verificar estructura de BD

```bash
poetry run python manage.py dbshell
# postgres=# \dt documentos_documentjob;
# postgres=# \q
```

---

## 🔄 Prueba 2: Sistema de Colas (Celery + Redis)

### Paso 1: Verificar conexión a Redis

```bash
redis-cli ping
# Debe retornar: PONG

# Verificar la estructura de Redis
redis-cli
> INFO stats
> KEYS celery*
> QUIT
```

### Paso 2: Iniciar Worker Celery

```bash
poetry run celery -A project worker --loglevel=debug
```

**Salida esperada:**

```bash
 -------------- celery@usuario v5.6.0 (sun-hills)
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

### Paso 3: Probar tarea de debug (en otra terminal)

```bash
poetry run python -c "
from project.celery import app
result = app.send_task('project.tasks.debug_task')
print('Task ID:', result.id)
"

# Verificar en el worker que procesa la tarea
```

---

## 📄 Prueba 3: Generación de Documentos

### Prueba 3a: Generar PDF (Contrato)

### Terminal 1: Iniciar Django

```bash
poetry run python manage.py runserver
```

### Terminal 2: Iniciar Worker

```bash
poetry run celery -A project worker --loglevel=info
```

### Terminal 3: Enviar documento

```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"
```

**Respuesta esperada:**

```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Documento en proceso de generación"
}
```

### Verificar estado

```bash
curl http://localhost:8000/api/documentos/status/550e8400-e29b-41d4-a716-446655440000/
```

### Esperar y ver cambio de estado

```json
{
  "status": "running",  // Luego: "completed"
  ...
}
```

### Descargar cuando complete

```bash
curl -o contrato.pdf \
  http://localhost:8000/api/documentos/download/550e8400-e29b-41d4-a716-446655440000/

# Verificar archivo
file contrato.pdf
# Debe mostrar: PDF document, version 1.4
```

---

### Prueba 3b: Generar Factura

```bash
# Enviar
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=invoice" \
  -F "file=@example_invoice.json"

# Copiar job_id y descargar cuando complete
curl -o factura.pdf \
  http://localhost:8000/api/documentos/download/<job_id>/
```

---

### Prueba 3c: Generar Certificado

```bash
# Enviar
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=certificate" \
  -F "file=@example_certificate.json"

# Descargar
curl -o certificado.pdf \
  http://localhost:8000/api/documentos/download/<job_id>/
```

---

## 🖥️ Prueba 4: Interfaz Web Drag & Drop

### Paso 1: Abrir navegador

```text
http://localhost:8000/api/documentos/upload/
```

### Paso 2: Probar funcionalidades

### Test 1: Seleccionar plantilla

- [ ] Seleccionar "Contrato"
- [ ] Verificar que el dropdown funciona

### Test 2: Drag & Drop

- [ ] Arrastra `example_contract.json` a la zona
- [ ] Verifica que aparezca el nombre del archivo
- [ ] Verifica que desaparece el error de validación

### Test 3: Click para seleccionar

- [ ] Haz clic en la zona
- [ ] Selecciona `example_invoice.json`
- [ ] Verifica que aparezca el nombre

### Test 4: Generar documento

- [ ] Selecciona "Factura"
- [ ] Selecciona `example_invoice.json`
- [ ] Haz clic en "Generar Documento"
- [ ] Verifica que aparezca spinner
- [ ] Espera a que complete
- [ ] Verifica que aparezca botón "Descargar"

### Test 5: Descargar

- [ ] Haz clic en "Descargar Documento"
- [ ] Verifica que se descargue el PDF

---

## 📊 Prueba 5: Monitoreo con Flower

### Paso 1: Iniciar Flower

```bash
poetry run celery -A project flower
```

### Paso 2: Acceder al dashboard

```text
http://localhost:5555
```

### Paso 3: Pruebas en Flower

### Test 1: Ver Workers

- [ ] Verificar que al menos 1 worker aparece
- [ ] Ver pool size (4 por defecto)
- [ ] Ver número de procesos

### Test 2: Monitor de Tareas

- [ ] Generar un documento
- [ ] Verificar que la tarea aparece en "Tasks"
- [ ] Ver tiempo de ejecución
- [ ] Ver estado (pending → received → started → succeeded)

### Test 3: Estadísticas

- [ ] Ir a "Stats"
- [ ] Ver: pool.timeouts, total tasks, etc.

### Test 4: Gráficos

- [ ] Generar varios documentos simultáneamente
- [ ] Ver gráfico de tareas por segundo
- [ ] Ver gráfico de workers online

---

## 🔐 Prueba 6: Panel Administrativo

### Paso 1: Acceder a Django Admin

```text
http://localhost:8000/admin/
```

**Credenciales:**

- Usuario: `admin`
- Contraseña: `admin123` (o lo que configuraste)

### Paso 2: Verificar modelos

**Documentos:**

- [ ] Click en "Trabajos de documentos"
- [ ] Debe mostrar lista de DocumentJob
- [ ] Cada item muestra: ID, tipo, estado, fecha

### Paso 3: Probar filtros

- [ ] Filtrar por "Estado: Completado"
- [ ] Filtrar por "Tipo de plantilla: Contrato"
- [ ] Filtrar por "Creado en: Hoy"

### Paso 4: Probar búsqueda

- [ ] Buscar por ID de trabajo
- [ ] Buscar por nombre de plantilla

### Paso 5: Descargar desde Admin

- [ ] Hacer clic en un trabajo completado
- [ ] Hacer clic en el link "Ver/Descargar"
- [ ] Verificar que se abre el PDF

### Paso 6: Acciones en lote

- [ ] Seleccionar varios trabajos fallidos
- [ ] Hacer clic en "Reintentar trabajos fallidos"
- [ ] Verificar que cambian a "Pendiente"

---

## ⚙️ Prueba 7: Manejo de Errores

### Prueba 7a: Archivo JSON inválido

```bash
# Crear archivo JSON malformado
echo '{"invalid json": }' > bad.json

# Enviar
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@bad.json"

# Esperar respuesta de error
# {"error": "Archivo JSON inválido: ..."}
```

### Prueba 7b: Plantilla no soportada

```bash
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=invalid_type" \
  -F "file=@example_contract.json"

# Esperar: "Plantilla no soportada"
```

### Prueba 7c: Campos faltantes en JSON

```bash
# JSON sin campos requeridos
echo '{"field1": "value1"}' > minimal.json

curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@minimal.json"

# Debe procesarse (con campos vacíos en el PDF)
# O mostrar error según validación
```

### Prueba 7d: Job ID no existe

```bash
curl http://localhost:8000/api/documentos/status/invalid-uuid/

# Esperar: {"error": "Trabajo no encontrado"} (404)
```

---

## 🔄 Prueba 8: Reintentos y Recuperación

### Paso 1: Simular fallo

```bash
# Mover plantilla temporalmente
mv templates_doc/contract.html.j2 templates_doc/contract.html.j2.bak

# Enviar documento
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"

# Esperar a que falle (status: failed)
```

### Paso 2: Restaurar y reintentar

```bash
# Restaurar plantilla
mv templates_doc/contract.html.j2.bak templates_doc/contract.html.j2

# Reintentar trabajos fallidos
poetry run python manage.py retry_failed_jobs --limit 5

# Verificar que ahora esté "pending"
curl http://localhost:8000/api/documentos/status/<job_id>/
```

### Paso 3: Verificar que se completa

```bash
# Esperar y verificar
curl http://localhost:8000/api/documentos/status/<job_id>/
# Debe mostrar: "status": "completed"
```

---

## 📦 Prueba 9: Con Docker

### Paso 1: Construir imágenes

```bash
docker-compose build
```

### Paso 2: Iniciar servicios

```bash
docker-compose up -d
```

### Paso 3: Esperar a que se inicie

```bash
# Ver logs
docker-compose logs -f web

# Esperar mensaje: "Quit the server with CONTROL-C"
```

### Paso 4: Verificar salud

```bash
docker-compose ps
# Todos deben estar "healthy" o "up"
```

### Paso 5: Probar endpoints

```bash
# Acceder a admin
curl http://localhost:8000/admin/
# Debe retornar HTML (200)

# Generar documento
curl -X POST http://localhost:8000/api/documentos/upload/ \
  -F "template_name=contract" \
  -F "file=@example_contract.json"
```

### Paso 6: Ver logs de worker

```bash
docker-compose logs worker
# Debe mostrar procesamiento de tareas
```

### Paso 7: Monitoreo con Flower

```bash
# Acceder a http://localhost:5555
curl http://localhost:5555
```

---

## 📈 Prueba 10: Carga y Estrés

### Prueba 10a: Generar múltiples documentos

```bash
#!/bin/bash
for i in {1..10}; do
  echo "Enviando documento $i..."
  curl -s -X POST http://localhost:8000/api/documentos/upload/ \
    -F "template_name=contract" \
    -F "file=@example_contract.json" | jq -r '.job_id'
done
```

### Prueba 10b: Monitorear en Flower

- [ ] Abrir <http://localhost:5555>
- [ ] Ver spike en "Tasks/sec"
- [ ] Ver todos los workers procesando
- [ ] Ver tiempo de ejecución promedio

### Prueba 10c: Verificar BD

```bash
# Contar documentos en BD
poetry run python manage.py shell
>>> from documentos.models import DocumentJob
>>> DocumentJob.objects.count()
# Debe ser >= 10
```

---

## 🧹 Limpieza Post-Pruebas

```bash
# Detener Docker
docker-compose down

# Eliminar archivos generados
rm -rf generated/*
rm -rf uploads/*

# Limpiar Redis
redis-cli FLUSHALL

# Limpiar BD (CUIDADO - borra todo)
poetry run python manage.py flush --no-input

# Reinicializar
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

---

## 📝 Checklist de Funcionalidades Probadas

**Desarrollo:**

- [ ] Django runserver funciona
- [ ] Admin panel accesible
- [ ] BD migrada correctamente

**Celery:**

- [ ] Redis funciona
- [ ] Worker inicia sin errores
- [ ] Tarea de debug ejecuta exitosamente

**API:**

- [ ] POST /upload/ con archivo
- [ ] GET /status/ retorna estado
- [ ] GET /download/ descarga PDF
- [ ] GET /jobs/ lista trabajos

**Web:**

- [ ] Upload.html carga
- [ ] Drag & drop funciona
- [ ] Forma valida inputs
- [ ] Spinner muestra durante generación
- [ ] Botón descargar aparece cuando completa

**Documentos:**

- [ ] PDF se genera correctamente
- [ ] Plantilla Jinja2 renderiza datos
- [ ] Archivo se guarda en disco

**Admin:**

- [ ] Login funciona
- [ ] Listar trabajos
- [ ] Filtrar por estado
- [ ] Buscar por ID
- [ ] Descargar PDF desde admin
- [ ] Reintentar trabajos fallidos

**Monitoreo:**

- [ ] Flower muestra workers
- [ ] Flower muestra tareas
- [ ] Flower muestra estadísticas
- [ ] Gráficos se actualizan

**Docker:**

- [ ] docker-compose up inicia todo
- [ ] Servicios pasan healthcheck
- [ ] API funciona desde contenedores
- [ ] Volúmenes persisten datos

---

## 📊 Comandos Útiles de Testing

```bash
# Ver logs en tiempo real
docker-compose logs -f web
docker-compose logs -f worker
docker-compose logs -f

# Ejecutar comando en contenedor
docker-compose exec web python manage.py shell
docker-compose exec worker celery -A project inspect active

# Abrir bash en contenedor
docker-compose exec web bash

# Inspeccionar tareas Celery
celery -A project inspect active
celery -A project inspect stats
celery -A project inspect revoked

# Listar tareas registradas
celery -A project inspect registered

# Monitorear en tiempo real
watch 'curl -s http://localhost:8000/api/documentos/jobs/ | jq'
```

---

**Última actualización:** Enero 2025
