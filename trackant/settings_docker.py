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

def _trusted_origin(value):
    origin = value.strip().rstrip('/')
    if origin and not origin.startswith(('http://', 'https://')):
        origin = 'http://' + origin
    return origin


CSRF_TRUSTED_ORIGINS = [
    o for o in (
        _trusted_origin(v)
        for v in os.environ.get('TRACKANT_CSRF_TRUSTED_ORIGINS', '').split(',')
    )
    if o
]
