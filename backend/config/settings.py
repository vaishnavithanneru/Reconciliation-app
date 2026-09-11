from pathlib import Path
import os
import dj_database_url


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-development-key"
)

# Local: DEBUG=True
# Render: Set DEBUG=False in Render environment variables
DEBUG = os.environ.get("DEBUG", "True") == "True"


# =========================================================
# ALLOWED HOSTS
# =========================================================

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# Render automatically provides this variable
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(
        os.environ["RENDER_EXTERNAL_HOSTNAME"]
    )


# =========================================================
# INSTALLED APPS
# =========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",

    # Our application
    "reconciliation",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    # CORS should be near the top
    "corsheaders.middleware.CorsMiddleware",

    # Security
    "django.middleware.security.SecurityMiddleware",

    # Serve static files in production
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # Django middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# URL CONFIGURATION
# =========================================================

ROOT_URLCONF = "config.urls"


# =========================================================
# WSGI
# =========================================================

WSGI_APPLICATION = "config.wsgi.application"


# =========================================================
# TEMPLATES
# =========================================================

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


# =========================================================
# DATABASE
# =========================================================
#
# LOCAL DEVELOPMENT
# -----------------
# If DATABASE_URL does not exist:
# Django uses SQLite.
#
# RENDER / PRODUCTION
# -------------------
# Render provides DATABASE_URL.
# Django connects to Render PostgreSQL.
#
# IMPORTANT:
# Do NOT use localhost PostgreSQL on Render.
#
# =========================================================

if os.environ.get("DATABASE_URL"):

    # Render PostgreSQL
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600
        )
    }

else:

    # Local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =========================================================
# PASSWORD VALIDATION
# =========================================================
#
# Authentication is not required for this assignment,
# so password validation is kept empty.
#
# =========================================================

AUTH_PASSWORD_VALIDATORS = []


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# CORS
# =========================================================
#
# Local React/Vite frontend:
#
# http://localhost:5173
# http://127.0.0.1:5173
#
# After Vercel deployment, add your Vercel URL here
# or configure it through an environment variable.
#
# =========================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


# =========================================================
# OPTIONAL FRONTEND URL FROM ENVIRONMENT
# =========================================================
#
# On Render you can later set:
#
# FRONTEND_URL=https://your-app.vercel.app
#
# =========================================================

FRONTEND_URL = os.environ.get("FRONTEND_URL")

if FRONTEND_URL:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}


# =========================================================
# PRODUCTION SECURITY
# =========================================================
#
# These are enabled only when DEBUG=False.
#
# =========================================================

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_BROWSER_XSS_FILTER = True

    SECURE_CONTENT_TYPE_NOSNIFF = True
