import os
from .settings import *

DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') + ['healthcheck.railway.app', '.up.railway.app']

# Postgres on Railway — uses DATABASE_URL if available, falls back to PG* vars
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', ''),
        conn_max_age=600,
        ssl_require=True,
    )
}

# Static files via whitenoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# CORS — add Railway domain
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'https://codegreen.netlify.app',
    'https://codegreenspace.netlify.app',
] + [f'https://{h}' for h in ALLOWED_HOSTS if h and not h.startswith('.')]
CORS_ALLOW_CREDENTIALS = True

# Allow cross-site cookies (Netlify → Railway)
SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'

# Google OAuth — injected via env vars so credentials aren't in code
SOCIALACCOUNT_PROVIDERS['google']['APP'] = {
    'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
    'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
    'key': '',
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
