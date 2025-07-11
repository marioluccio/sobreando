"""
Local development settings for Sombreando
"""

from .base import *

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sombreando_dev',
        'USER': 'sombreando',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Disable HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
]

# Logging for development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['sombreando']['level'] = 'DEBUG'

# Cache settings for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Media files in development
MEDIA_ROOT = BASE_DIR / 'media'

# Static files in development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

