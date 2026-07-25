import os
from .settings import *

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE[1:]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get('TRACKANT_CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]
