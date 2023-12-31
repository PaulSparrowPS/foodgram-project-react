import os
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = (
    'SECRET_KEY',
    'test')

DEBUG = os.getenv('DEBUG', default='True') == 'True'

ALLOWED_HOSTS = ['127.0.0.1',
                 'localhost',
                 'backend',
                 '130.193.55.82',
                 'paulsparrow3.ddns.net']

AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'users.apps.UsersConfig',
    'recipes.apps.RecipesConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv(
            'DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': os.getenv(
            'POSTGRES_DB',
            default='postgres'),
        'USER': os.getenv(
            'POSTGRES_USER',
            default='postgres'),
        'PASSWORD': os.getenv(
            'POSTGRES_PASSWORD',
            default='postgres'),
        'HOST': os.getenv(
            'DB_HOST',
            default='db'),
        'PORT': os.getenv(
            'DB_PORT',
            default='5432'),
    }}

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

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.LimitPageNumberPagination',
    'PAGE_SIZE': 6,
}

CSRF_TRUSTED_ORIGINS = ['https://127.0.0.1:9000/', 'https://localhost/',
                        'https://130.193.55.82/', 'https://paulsparrow3.ddns.net/',
                        'https://*.ddns.net/', 'https://ddns.net/', 'http://*.ddns.net/', 'http://ddns.net/',
                        'http://127.0.0.1:9000/', 'http://localhost/',
                        'http://130.193.55.82/', 'http://paulsparrow3.ddns.net/',
                        'https://paulsparrow3.ddns.net/admin/login/?next=/admin/',
                        'https://paulsparrow3.ddns.net/admin/'
                        ]
