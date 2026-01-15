import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# In production, DEBUG should be explicitly set to 'False' via environment variable
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Parse ALLOWED_HOSTS from environment variable, default to localhost for dev
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'users',
    'recycling',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dropme.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'dropme.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'dropme_db'),
        'USER': os.getenv('DB_USER', 'ali_emad'),
        'PASSWORD': os.getenv('DB_PASSWORD', '00000'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling for production
    }
}

DEFAULT_USER_MODEL = 'users.User'
AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Drop Me Recycling API',
    'DESCRIPTION': 'Backend API for Drop Me recycling machine management',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

###################################################################################

# Business Rules Configuration
RECYCLING_RULES = {
    'PLASTIC': {'points': 10, 'material_type': 'plastic'},
    'GLASS': {'points': 15, 'material_type': 'glass'},
    'ALUMINUM': {'points': 12, 'material_type': 'aluminum'},
    'PAPER': {'points': 5, 'material_type': 'paper'},
}

# Business Rules for rate limiting
MAX_TRANSACTIONS_PER_DAY=50
MIN_TRANSACTION_INTERVAL=5

TRANSACTION_LIMITS = {
    'max_transactions_per_day': MAX_TRANSACTIONS_PER_DAY,
    'min_transaction_interval': timedelta(minutes=MIN_TRANSACTION_INTERVAL),
}