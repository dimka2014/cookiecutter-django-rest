import datetime
import environ
import os
import json

ROOT_DIR = environ.Path(__file__) - 3  # ({{cookiecutter.project_slug}}/config/settings/base.py - 3 = {{cookiecutter.project_slug}}/)
APPS_DIR = ROOT_DIR.path('{{cookiecutter.project_slug}}')

MEDIA_ROOT = str(ROOT_DIR.path('media'))
MEDIA_URL = '/media/'

STATIC_URL = '/static-backend/'
STATIC_ROOT = str(ROOT_DIR.path('static'))

env = environ.Env()

SECRET_KEY = env('SECRET_KEY', default='secret')

ALLOWED_HOSTS = ['*']

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_swagger',
    'django_countries',
    'django_cron',
    'model_fields',
    'authtools',
    {% if cookiecutter.social_authentication == 'y' -%}
    'social_django',
    'rest_social_auth',
    {%- endif %}
]

LOCAL_APPS = [
    '{{cookiecutter.project_slug}}.core.apps.CoreConfig',
    '{{cookiecutter.project_slug}}.users.apps.UsersConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

DEBUG = env('DEBUG', default=False)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATABASES = {
    'default': env.db(default='sqlite:///development.sqlite3')
}

EMAIL_CONFIG = env.email_url('EMAIL_URL', default='filemail://mails')
vars().update(EMAIL_CONFIG)

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

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

CRON_CLASSES = []

AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 5,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': '{{cookiecutter.project_slug}}.core.pagination.StandardResultsSetPagination',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        '{{cookiecutter.project_slug}}.users.authentication.ImpersonatebleJWTAuthentication',
    ),
    'COERCE_DECIMAL_TO_STRING': False
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
}

{% if cookiecutter.social_authentication == 'y' -%}
AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)    

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.debug.debug',
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_FACEBOOK_KEY = env.str('FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = env.str('FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_USER_FIELDS = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'ru_RU',
    'fields': 'id, name, email'
}
{%- endif %}
