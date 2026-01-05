"""
Settings configuration for the Django project.

Include all necessary settings for the application,
database, middleware, installed apps, templates,
static files, and third-party integrations.
"""

from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    'DJANGO_SECRET_KEY',
    default='django-insecure-development-key-change-in-production'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())


# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'corsheaders',
    'widget_tweaks',
    
    # Aplicaciones locales
    'docs.apps.DocsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'docs' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME', default='djangodb'),
        'USER': config('DATABASE_USER', default='djangouser'),
        'PASSWORD': config('DATABASE_PASSWORD', default='secretpassword'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Directory where collectstatic will copy all static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional directories to look for static files
STATICFILES_DIRS = [
    BASE_DIR / 'docs' / 'static',
]


# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Generated documents
GENERATED_DOCUMENTS_DIR = BASE_DIR / 'generated'
UPLOADED_FILES_DIR = BASE_DIR / 'uploads'

# Crear directorios si no existen
GENERATED_DOCUMENTS_DIR.mkdir(exist_ok=True)
UPLOADED_FILES_DIR.mkdir(exist_ok=True)


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8000',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True


# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

# Celery broker (Redis)
CELERY_BROKER_URL = config(
    'CELERY_BROKER_URL',
    default='redis://localhost:6379/0'
)

# Celery result backend (Redis)
CELERY_RESULT_BACKEND = config(
    'CELERY_RESULT_BACKEND',
    default='redis://localhost:6379/1'
)

# Configuración de serialización
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Configuración de retries y timeouts
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # segundos

# Configuración de colas
CELERY_TASK_ROUTES = {
    'docs.tasks.generate_pdf_task': {'queue': 'documents'},
    'docs.tasks.generate_docx_task': {'queue': 'documents'},
    'docs.tasks.generate_json_task': {'queue': 'documents'},
}

CELERY_QUEUES = {
    'default': {
        'exchange': 'default',
        'binding_key': 'default'
    },
    'documents': {
        'exchange': 'documents',
        'binding_key': 'documents'
    },
}

# Time limit para tareas (segundos)
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutos

# Resultado expire time (segundos)
CELERY_RESULT_EXPIRES = 3600  # 1 hora

# Logging
CELERY_LOGLEVEL = config('CELERY_LOGLEVEL', default='info')


# ============================================================================
# APLICACIÓN ESPECÍFICA
# ============================================================================

# Directorio de plantillas Jinja2
TEMPLATES_DOC_DIR = BASE_DIR / 'templates_doc'

# Tipos de docs soportados
SUPPORTED_DOCUMENT_TYPES = {
    'contract': 'contract.html.j2',
    'invoice': 'invoice.html.j2',
    'certificate': 'certificate.html.j2',
    "docx_contract": "contract.docx",
}

# Configuración de WeasyPrint
WEASYPRINT_FONT_SIZES = {
    'small': '12px',
    'normal': '14px',
    'large': '16px',
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755