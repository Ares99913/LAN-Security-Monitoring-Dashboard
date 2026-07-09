"""
Django settings for server_509 project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-key-before-production"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "monitor.apps.MonitorConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "monitor.middleware.BruteForceMiddleware",
]

ROOT_URLCONF = "server_509.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server_509.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE"      : "django.db.backends.postgresql",
        "NAME"        : "lan_monitor_db",
        "USER"        : "lan_monitor_user",
        "PASSWORD"    : "lan_monitor_pass",
        "HOST"        : "127.0.0.1",
        "PORT"        : "5432",
        "CONN_MAX_AGE": 60,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Asia/Kolkata"
USE_I18N      = True
USE_TZ        = True

STATIC_URL  = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

CSRF_TRUSTED_ORIGINS = [
    "http://10.107.159.30:8000",
    "http://localhost:8000",
]

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

os.makedirs(BASE_DIR / 'logs', exist_ok=True)
LOGGING = {
    'version'                 : 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level'   : 'ERROR',
            'class'   : 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers' : ['file'],
            'level'    : 'ERROR',
            'propagate': True,
        },
    },
}
