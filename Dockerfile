# Dockerfile
FROM python:3.12-slim

LABEL maintainer="alvaro.pri.2003@gmail.com" \
      description="Django + Celery + Redis"

# Install system dependencies
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

# Copy requirements
COPY requirements.txt /app/

# Install python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . /app

# Make media and staticfiles directories with proper permissions
RUN mkdir -p /app/media/uploads /app/media/generated /app/staticfiles && \
    chmod -R 777 /app/media && \
    chmod -R 777 /app/staticfiles

# Expose ports for Django and Celery Flower
EXPOSE 8000 5555

# Start Gunicorn server
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
