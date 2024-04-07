"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from django.contrib.auth import get_user_model
from datetime import timedelta
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

BASE_URL = 'http://localhost:8080'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-16gw%urziwr2)!1k_a4%x=7his@)u7h51y)ro-6sch!u73^jc5'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# AUTH
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = ('users.backends.AuthBackend',)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',   # OAuth2, JWT
    ),
    'DEFAULT_PERMITIONS_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

CORS_ALLOWED_ORIGINS = ['http://localhost:8080', 'http://127.0.0.1:8080', 'http://127.0.0.1:8000']

CART_SESSION_ID = 'cart'

# Application definition

INSTALLED_APPS = [
    'corsheaders',                  # I always put it first here and in Middleware!
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',

    # 3rd party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'social_django',
    'djoser',
    'parler',
    'mptt',
    'rosetta',
    'graphene_django',
    'graphql_jwt.refresh_token',
    'taggit',
    'star_ratings',
    'dynamic_preferences',
    'dynamic_preferences.users.apps.UserPreferencesConfig',
    'debug_toolbar',
    'django_celery_beat',
    # 'storages',
    'django_admin_inline_paginator',

    # Project apps:
    'users',
    'profiles',
    'aggregator',
    # 'telegram_bot',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # IMPORTANT: CORS policies has to go before other entries
    'corsheaders.middleware.CorsMiddleware',
    # IMPORTANT: Essential when using django_social
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Crucial for social login to work!
                'social_django.context_processors.backends', 
                'social_django.context_processors.login_redirect',
                'dynamic_preferences.processors.global_preferences',
                # Additional
                'backend.context_processors.extra_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aggregatordb',
        'USER': 'aggregatoruser',
        'PASSWORD': 'qw12345',
        'HOST': 'postgres14_container',
        'PORT': 5432,
    },
    # 'sqlite': {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('ru', _('Russian')),
    ('uk', _('Ukrainian')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
# TIME_ZONE = 'Europe/Kiev'

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
                
# django-parler settings
PARLER_LANGUAGES = {
    None: (
        {'code': 'en'},
        {'code': 'ru'},
        {'code': 'uk'},
    ),
    'default': {
        'fallback': 'en',
        'hide_untranslated': False,
    }
}

TAGGIT_CASE_INSENSITIVE = True

STAR_RATINGS_ANONYMOUS = False

DYNAMIC_PREFERENCES = {
    # a python attribute that will be added to model instances with preferences
    # override this if the default collide with one of your models attributes/fields
    'MANAGER_ATTRIBUTE': 'preferences',

    # The python module in which registered preferences will be searched within each app
    'REGISTRY_MODULE': 'preferences_registry',

    # Allow quick editing of preferences directly in admin list view
    # WARNING: enabling this feature can cause data corruption if multiple users
    # use the same list view at the same time, see https://code.djangoproject.com/ticket/11313
    'ADMIN_ENABLE_CHANGELIST_FORM': False,

    # Customize how you can access preferences from managers. The default is to
    # separate sections and keys with two underscores. This is probably not a settings you'll
    # want to change, but it's here just in case
    'SECTION_KEY_SEPARATOR': '__',

    # Use this to disable auto registration of the GlobalPreferenceModel.
    # This can be useful to register your own model in the global_preferences_registry.
    'ENABLE_GLOBAL_MODEL_AUTO_REGISTRATION': True,

    # Use this to disable caching of preference. This can be useful to debug things
    'ENABLE_CACHE': True,

    # Use this to select which chache should be used to cache preferences. Defaults to default.
    'CACHE_NAME': 'default',

    # Use this to disable checking preferences names. This can be useful to debug things
    'VALIDATE_NAMES': True,
}

# AMAZON S3
# AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
# AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
# AWS_STORAGE_BUCKET_NAME = 'product.aggregator'
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# AWS_S3_OBJECT_PARAMETERS = {
#    'CacheControl': 'max-age=86400',
# }

# AWS_STATIC_LOCATION = 'static'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)

# DEFAULT_FILE_STORAGE = 'backend.storage_backends.MediaStorage'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GRAPHENE = {
    'SCHEMA': 'backend.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
        'graphene_django.debug.DjangoDebugMiddleware',
    ]
}

GRAPHQL_JWT = {
    "JWT_ALLOW_ARGUMENT": True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_EXPIRATION_DELTA': timedelta(minutes=15),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'SEND_ACTIVATION_EMAIL': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': [
#        'http://localhost:8000/social-auth/complete/google-oauth2/',
#        'http://localhost:8000/social-auth/complete/facebook/',
    ],
    'TOKEN_MODEL': None, # We use only JWT
    'ACTIVATION_URL': 'auth/verify/{uid}/{token}/',
}

REST_SOCIAL_VERBOSE_ERRORS = True

SOCIAL_AUTH_FACEBOOK_KEY = 'FACEBOOK_KEY'
SOCIAL_AUTH_FACEBOOK_SECRET = 'FACEBOOK_SECRET'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]  # optional
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'ru_RU'}  # optional

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'GOOGLE_KEY'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'GOOGLE_SECRET'
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', ]
# Fields that get saved in JSON string along with the token
# To see the data add social_django to installed apps in order
# to access this in /admin/ site
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ['picture', 'locale', 'uuid'] 


LOGIN_URL = 'home'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'

AUTHENTICATION_BACKENDS = (
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
    # Important for accessing admin with django_social
#    'users.oauth.google.CustomGoogleOAuth2',
    'users.oauth.facebook.CustomFacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    #'social_core.backends.facebook.FacebookOAuth2',
    #'social_core.backends.instagram.InstagramOAuth2',
    #'social_core.backends.apple.AppleIdAuth',
    # and maybe some others ...
)

SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    #'account.authentication.create_profile',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
]
                        
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    'AUTH_HEADER_TYPES': ('JWT', 'Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',
#        'SocialDjango.token.CustomJWTToken'
    ),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

#    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
#    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
#    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
#    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
#    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

# CELERY
REDIS_URL = 'redis://redis7_container:6379/0'
BROKER_URL = REDIS_URL
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_DEFAULT_QUEUE = 'default'

# TELEGRAM
TELEGRAM_TOKEN = ''
TELEGRAM_BOT_USERNAME = ''
# LOGGING
ENABLE_DECORATOR_LOGGING = False

SILPO_ID = 1
SILPO_CATEGORY = 'susheni-frukty-gryby-gorikhy-382'
SILPO_PRODUCTS_URL = 'uk/branches/00000000-0000-0000-0000-000000000000/products'
SILPO_IMAGES_URL = 'https://images.silpo.ua/products/300x300/webp/'
SILPO_MAX_PRODUCTS_LIMIT = 100

ROZETKA_ID = 2
ROZETKA_LIST_PRODUCTS_URL = 'goods/get'
ROZETKA_PRODUCTS_URL = 'goods/getDetails'

TAVRIA_ID = 3
TAVRIA_PRODUCTS_URL = 'product'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/main.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django_request.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {  # Stop SQL debug from logging to main logger
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    },
}

INTERNAL_IPS = [
    '127.0.0.1',
]