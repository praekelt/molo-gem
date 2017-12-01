"""Django settings for use within the docker container."""

from django.core.exceptions import ImproperlyConfigured
from os import environ

import dj_database_url

from .production import *


# Disable debug mode

DEBUG = False

default_secret_key = 'please-change-me'
SECRET_KEY = environ.get('SECRET_KEY') or default_secret_key

if SECRET_KEY == default_secret_key:
    raise ImproperlyConfigured('Secure SECRET_KEY not provided')

PROJECT_ROOT = (
    environ.get('PROJECT_ROOT') or dirname(dirname(abspath(__file__))))

SERVICE_DIRECTORY_API_BASE_URL = environ.get(
    'SERVICE_DIRECTORY_API_BASE_URL', '')
SERVICE_DIRECTORY_API_USERNAME = environ.get(
    'SERVICE_DIRECTORY_API_USERNAME', '')
SERVICE_DIRECTORY_API_PASSWORD = environ.get(
    'SERVICE_DIRECTORY_API_PASSWORD', '')

GOOGLE_PLACES_API_SERVER_KEY = environ.get(
    'GOOGLE_PLACES_API_SERVER_KEY', '')

RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

CAS_SERVER_URL = environ.get('CAS_SERVER_URL') or ''

COMPRESS_OFFLINE = True

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///%s' % (join(PROJECT_ROOT, 'gemmolo.db'),))}

MEDIA_ROOT = join(PROJECT_ROOT, 'media')

STATIC_ROOT = join(PROJECT_ROOT, 'static')

LOCALE_PATHS = (
    join(PROJECT_ROOT, "locale"),
)
