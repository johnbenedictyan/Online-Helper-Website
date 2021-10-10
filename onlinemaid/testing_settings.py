"""
Django settings for onlinemaid project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

# Python libraries
import os
import sys
import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration
from pathlib import Path

# 3rd party libraries
import dj_database_url
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration


from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DJANGO_DEBUG', '0')) == 1

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')
ADMIN_IP_WHITELIST = os.environ.get(
    'ADMIN_IP_WHITELIST',
    '127.0.0.1'
).split(',')


# Application definition

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.postgres',

    # 3rd party packages
    # 'captcha',
    # 'extra_views',
    'crispy_forms',
    'django_filters',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'social_django',
    'storages',

    # Our apps
    'accounts.apps.AccountsConfig',
    'advertisement',
    'agency.apps.AgencyConfig',
    'dashboard',
    'employer_documentation.apps.EmployerDocumentationConfig',
    'maid.apps.MaidConfig',
    'payment.apps.PaymentConfig',
    'shortlist',
    'website',
    'enquiry',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # django_otp requirement
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'onlinemaid.middleware.AdminAccessIPWhiteListMiddleware'
]

ROOT_URLCONF = 'onlinemaid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'onlinemaid.context_processors.authority',
                'onlinemaid.context_processors.cartcount',
                'onlinemaid.context_processors.enquiry_form',
                'onlinemaid.context_processors.dashboard_side_nav',
                'onlinemaid.context_processors.page_bar_url_helper',
                'onlinemaid.context_processors.meta_formatter'
            ],
        },
    },
]

WSGI_APPLICATION = 'onlinemaid.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "main",
        'USER': "doadmin",
        'PASSWORD': "Azz7yqSlPPKuHfSE",
        'HOST': "db-postgresql-sgp1-32222-do-user-6024916-0.b.db.ondigitalocean.com",
        'PORT': "25060",
        'DISABLE_SERVER_SIDE_CURSORS': True,
        'OPTIONS': {'sslmode': 'require'},
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

USE_S3 = os.environ.get('USE_S3') == 'TRUE'

if USE_S3:
    # AWS Settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_IS_GZIPPED = True
    # s3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'onlinemaid.storage_backends.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'onlinemaid.storage_backends.PublicMediaStorage'
    # s3 private media settings
    PRIVATE_MEDIA_LOCATION = 'private'
    PRIVATE_FILE_STORAGE = 'onlinemaid.storage_backends.PrivateMediaStorage'
else:
    STATIC_URL = '/staticfiles/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/mediafiles/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# Authentication settings

AUTH_USER_MODEL = 'accounts.User'

SOCIAL_AUTH_USER_MODEL = 'accounts.User'
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['email']
AUTHENTICATION_BACKENDS = [
    # Facebook Auth
    'social_core.backends.facebook.FacebookOAuth2',
    # Google Auth
    'social_core.backends.google.GoogleOAuth2',
    # Default Django Accounts Auth
    'django.contrib.auth.backends.ModelBackend',
]
SOCIAL_AUTH_URL_NAMESPACE = 'socialauth'
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, email',
}
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get(
    'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'
)

# python-social-auth pipeline override
# https://python-social-auth.readthedocs.io/en/latest/pipeline.html

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    # 'social_core.pipeline.user.get_username',
    'onlinemaid.pipeline.get_username',
    'social_core.pipeline.user.create_user',
    'onlinemaid.pipeline.create_employer',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_URL = 'sign_in'
# LOGIN_REDIRECT_URL = 'home'


# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_HOST_SALES_USER = os.environ.get('EMAIL_HOST_SALES_USER')

MESSAGE_TAGS = {
    messages.DEBUG: 'text-info',
    messages.INFO: 'text-info',
    messages.SUCCESS: 'text-success',
    messages.WARNING: 'text-warning',
    messages.ERROR: 'text-danger',
}

# Django-OTP
OTP_TOTP_ISSUER = 'om-django-otp'

# Stripe
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

# Pycryptodome Key
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

# django.contrib.sites.models.Site
SITE_ID = 1

# Pagination
MAID_PAGINATE_BY = 12
AGENCY_PAGINATE_BY = 12
DASHBOARD_PAGINATE_BY = 10

# Django Recaptcha Settings
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_REQUIRED_SCORE = os.environ.get('RECAPTCHA_REQUIRED_SCORE')
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# Custom Django Pages
handler403 = 'website.views.Error403View'
handler404 = 'website.views.Error404View'
handler500 = 'website.views.Error500View'

# Django Security
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600

# Account UUID V5 Name and Namespace
ACCOUNT_UUID_NAMESPACE = os.environ.get('ACCOUNT_UUID_NAMESPACE')

# Django Other Settings
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ADMIN_ID = os.environ.get('ADMIN_ID')
