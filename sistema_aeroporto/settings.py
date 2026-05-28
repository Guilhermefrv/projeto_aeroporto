"""
Django settings for sistema_aeroporto project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ──────────────────────────────────────────
#  Segurança
# ──────────────────────────────────────────

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8+@nwji8cuwaqa48yp&5^f*@6boswwevy=&7%36ycsj8gfq97q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# ──────────────────────────────────────────
#  Modelo de Usuário Customizado
# ──────────────────────────────────────────

AUTH_USER_MODEL = 'skybridgeapp.UsuarioCustomizado'


# ──────────────────────────────────────────
#  Redirecionamentos de autenticação
# ──────────────────────────────────────────

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# ──────────────────────────────────────────
#  Apps instalados
# ──────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'skybridgeapp',
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

ROOT_URLCONF = 'sistema_aeroporto.urls'

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
                'skybridgeapp.context_processors.notificacoes_nao_lidas',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_aeroporto.wsgi.application'


# ──────────────────────────────────────────
#  Banco de Dados — PostgreSQL
# ──────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'skybridge',
        'USER': 'postgres',
        'PASSWORD': 'admin',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


# ──────────────────────────────────────────
#  Validação de senhas
# ──────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ──────────────────────────────────────────
#  Internacionalização
# ──────────────────────────────────────────

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ──────────────────────────────────────────
#  Arquivos estáticos
# ──────────────────────────────────────────

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
