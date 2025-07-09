from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-4v@)8#r3&!$=5g1@)9^+q2j0z6b3@7xk#(4f!$=5g1@)9^+q2j0z6b3@7xk#",
)

DEBUG = os.getenv("DJANGO_DEBUG", "False")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

# Django Debug Toolbar settings
INTERNAL_IPS = os.getenv("INTERNAL_IPS", "localhost,127.0.0.1,0.0.0.0").split(",")


# Application definition

PROJECT_APPS = [
    "accounts",
    "address",
    "core",
    "skin_conditions",
    "skin_forms",
    "health_unit",
    "profile_forms",
]

THIRD_PARTY_APPS = [
    "django_filters",
    "corsheaders",
    "debug_toolbar",
    "drf_yasg",
    "storages",
]

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

DJANGO_REST_FRAMEWORK_APPS = [
    "rest_framework",
]

INSTALLED_APPS = (
    DJANGO_APPS + DJANGO_REST_FRAMEWORK_APPS + THIRD_PARTY_APPS + PROJECT_APPS
)

PROJECT_MIDDLEWARE = []

THIRD_PARTY_MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

DJANGO_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DJANGO_REST_FRAMEWORK_MIDDLEWARE = []

MIDDLEWARE = (
    DJANGO_MIDDLEWARE
    + DJANGO_REST_FRAMEWORK_MIDDLEWARE
    + THIRD_PARTY_MIDDLEWARE
    + PROJECT_MIDDLEWARE
)

ROOT_URLCONF = "dermalert.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dermalert.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Configuração do banco de dados
if os.getenv("POSTGRES_DB"):
    # Para desenvolvimento e produção com PostgreSQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "django_db"),
            "USER": os.getenv("POSTGRES_USER", "django_user"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "django_password"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    # Fallback para SQLite em desenvolvimento local
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

AWS_ACCESS_KEY_ID       = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY   = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
AWS_S3_ENDPOINT_URL     = os.getenv("AWS_S3_ENDPOINT_URL", "http://minio:9000")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "dermalert")

AWS_S3_REGION_NAME      = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_URL_PROTOCOL     = os.getenv("AWS_S3_URL_PROTOCOL", "http:")
AWS_S3_CUSTOM_DOMAIN    = os.getenv("AWS_S3_CUSTOM_DOMAIN", "localhost:9000")
AWS_QUERYSTRING_AUTH    = False
AWS_DEFAULT_ACL         = "public-read"

STATIC_URL  = f"{AWS_STORAGE_BUCKET_NAME}/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

COMMON_S3_OPTS = {
    "bucket_name":      AWS_STORAGE_BUCKET_NAME,
    "endpoint_url":     AWS_S3_ENDPOINT_URL,
    "access_key":       AWS_ACCESS_KEY_ID,
    "secret_key":       AWS_SECRET_ACCESS_KEY,
    "region_name":      AWS_S3_REGION_NAME,
    "addressing_style": AWS_S3_ADDRESSING_STYLE,
    "querystring_auth": AWS_QUERYSTRING_AUTH,
    "default_acl":      AWS_DEFAULT_ACL,
}

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            **COMMON_S3_OPTS,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            **COMMON_S3_OPTS,
            "location": STATIC_URL,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN,
            "url_protocol": AWS_S3_URL_PROTOCOL,
        },
    },
}


if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Rest Framework settings

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
    "DEFAULT_FILTER_BACKENDS": "django_filters.rest_framework.DjangoFilterBackend",
}


AUTH_USER_MODEL = "accounts.User"
USERNAME_FIELD = "cpf"

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = []

