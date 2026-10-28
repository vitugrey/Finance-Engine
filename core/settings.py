"""
Django settings for GreyWorks Finance project.
"""

import logging
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

DB_DIR = BASE_DIR / 'databases'
DB_DIR.mkdir(parents=True, exist_ok=True)


def _get_secret_key() -> str:
    env_key = os.getenv('SECRET_KEY')
    if env_key:
        return env_key
    secret_file = DB_DIR / '.django_secret'
    if secret_file.exists():
        return secret_file.read_text(encoding='utf-8').strip()
    logging.warning("Generating ephemeral SECRET_KEY. Instance-isolated!")
    generated = secrets.token_hex(32)
    try:
        secret_file.write_text(generated, encoding='utf-8')
    except OSError:
        pass
    return generated


SECRET_KEY = _get_secret_key()

DEBUG = os.getenv('DEBUG', 'True').lower() in ('1', 'true', 'yes')

_allowed = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = ['*'] if _allowed == '*' else [h.strip() for h in _allowed.split(',')]

# Security Headers
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_CONTENT_TYPE_NOSNIFF = True
# TODO(security): Add strict CSP middleware and OAuth/MFA if deployed as a multi-tenant cloud service.


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Apps do projeto
    'budget',
    'investments',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


def _resolve_db_file(db_dir: Path) -> Path:
    env_name = os.getenv('DB_FILENAME')
    if env_name:
        return db_dir / Path(env_name).name
    return db_dir / 'greyworks-finance.db'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _resolve_db_file(DB_DIR),
    }
}


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


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

USE_L10N = False
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
DECIMAL_SEPARATOR = '.'

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
