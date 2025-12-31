# Dockerfile
FROM python:3.12-slim

LABEL maintainer="alvaro.pri.2003@gmail.com" \
      description="Django + Celery + Redis"

# Instalar dependencias del sistema (incluyendo WeasyPrint)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgobject-2.0-0 \
    libglib2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt /app/

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el código de la app
COPY . /app

# Exponer puertos
EXPOSE 8000 5555

# Arranque por defecto con gunicorn
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
