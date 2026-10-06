import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = Path.home() / '.trackant'
DATA_DIR.mkdir(exist_ok=True)

SECRET_KEY_FILE = DATA_DIR / 'secret_key'


def _load_secret_key():
    env_key = os.environ.get('TRACKANT_SECRET_KEY')
    if env_key:
        return env_key
    if SECRET_KEY_FILE.exists():
        return SECRET_KEY_FILE.read_text().strip()
    key = get_random_secret_key()
    SECRET_KEY_FILE.write_text(key)
    return key


SECRET_KEY = _load_secret_key()

DEBUG = os.environ.get('TRACKANT_DEBUG', 'True').lower() in ('true', '1', 'yes')

def _allowed_host(value):
    return value.strip().removeprefix('http://').removeprefix('https://').rstrip('/')


ALLOWED_HOSTS = [
    h for h in (
        _allowed_host(v)
        for v in os.environ.get('TRACKANT_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    )
    if h
]
if DEBUG:
    ALLOWED_HOSTS.extend(['*', '.local'])

VERSION_FILE = BASE_DIR / 'VERSION'
TRACKANT_VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else 'dev'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'django_htmx',
    'django_filters',
    'widget_tweaks',
    'crispy_forms',
    'crispy_tailwind',
    # Apps
    'users',
    'finances',
    'goals',
    'debts',
    'budgets',
    'subscriptions',
    'splits',
    'ants',
    'backups',
    'api',
    'installments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.ColonyMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'trackant.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.tab_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'trackant.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'users.CustomUser'

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'es-AR'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session configuration for Docker/proxy deployments
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks
SESSION_COOKIE_SAMESITE = 'Lax'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Conversión de moneda
EXCHANGE_API_URL = os.environ.get('TRACKANT_EXCHANGE_API_URL', 'https://open.er-api.com/v6/latest/USD')
EXCHANGE_INTERVAL_HOURS = int(os.environ.get('TRACKANT_EXCHANGE_INTERVAL_HOURS', 6))
