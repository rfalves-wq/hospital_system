"""
Django settings for hospital_system project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(nome, padrao=False):
    valor = os.environ.get(nome)

    if valor is None:
        return padrao

    return valor.strip().lower() in {"1", "true", "sim", "yes", "on"}

# Segurança
SECRET_KEY = os.environ.get("HOSPITAL_SECRET_KEY", "troque-esta-chave-em-producao")

DEBUG = env_bool("HOSPITAL_DEBUG", True)

_ALLOWED_HOSTS = os.environ.get(
    "HOSPITAL_ALLOWED_HOSTS",
    "localhost,127.0.0.1,0.0.0.0,*",
)
ALLOWED_HOSTS = [
    host.strip()
    for host in _ALLOWED_HOSTS.split(",")
    if host.strip()
]

# Aplicações instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'unidades',
    'dashboard',
    'acolhimento',
    'recepcao',
    'classificacao',
    "medico",
    "laboratorio",
    "imagem",
    "medicacao",
    "farmacia",
    "internacao",
    "prontuario",
    "tecnologia",
    "painel",
    
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.LoginPermissaoMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hospital_system.urls'

# Templates
TEMPLATE_CONTEXT_PROCESSORS = [
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'accounts.context_processors.acessos_usuario',
]

USAR_CACHE_TEMPLATES = env_bool("HOSPITAL_TEMPLATE_CACHE", not DEBUG)

TEMPLATE_OPTIONS = {
    'context_processors': TEMPLATE_CONTEXT_PROCESSORS,
}

if USAR_CACHE_TEMPLATES:
    TEMPLATE_OPTIONS['loaders'] = [
        (
            'django.template.loaders.cached.Loader',
            [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        )
    ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': not USAR_CACHE_TEMPLATES,
        'OPTIONS': TEMPLATE_OPTIONS,
    },
]

WSGI_APPLICATION = 'hospital_system.wsgi.application'

# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'timeout': 20,
        },
    }
}

# Cache local para reduzir consultas repetidas e acelerar sessoes em rede.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hospital-system-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 5000,
        },
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Senhas
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

# Idioma e Fuso Horário
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

# Horário do Brasil gravado diretamente no banco
USE_TZ = False

# Arquivos estáticos
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Usuário personalizado
AUTH_USER_MODEL = 'accounts.Usuario'

# Login
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
