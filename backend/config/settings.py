"""
CoinHub Django Settings
"""
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost").split(",")

# ── Installed Apps ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Jazzmin must come before django.contrib.admin
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_filters",
    # CoinHub apps
    "apps.core",
    "apps.accounts",
    "apps.catalog",
    "apps.orders",
    "apps.payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ── Database ───────────────────────────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=''),
        conn_max_age=600,
        ssl_require=True
    )
}

# Fallback for local development if DATABASE_URL is not set
if not DATABASES['default']:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='coinhub'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }

# ── Auth ───────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Internationalisation ───────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# ── Static / Media ────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [] 

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Django REST Framework ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    # Defined auth classes to prevent implicit session hijacking
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("THROTTLE_ANON", default="100/day"),
        "user": config("THROTTLE_USER", default="1000/day"),
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS", default="http://localhost:8080,http://127.0.0.1:8080"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ── CSRF TRUSTED ORIGINS ──────────────────────
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", 
    default="http://localhost:8080,http://127.0.0.1:8080"
).split(",")

# ── Daraja (M-Pesa) ───────────────────────────────────────────────────────────
DARAJA = {
    "CONSUMER_KEY": config("DARAJA_CONSUMER_KEY"),
    "CONSUMER_SECRET": config("DARAJA_CONSUMER_SECRET"),
    "SHORTCODE": config("DARAJA_SHORTCODE"),
    "TILL_NUMBER": config("DARAJA_TILL_NUMBER"),
    "PASSKEY": config("DARAJA_PASSKEY"),
    "CALLBACK_URL": config("DARAJA_CALLBACK_URL"),
    "ENV": config("DARAJA_ENV", default="sandbox"),
}

# ── Jazzmin Admin UI ──────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "CoinHub Admin",
    "site_header": "CoinHub",
    "site_brand": "CoinHub",
    "welcome_sign": "Welcome to CoinHub Admin",
    "copyright": "CoinHub Ltd",
    "search_model": ["orders.Order", "payments.Payment"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API Docs", "url": "/api/", "new_window": True},
    ],
    "usermenu_links": [
        {"name": "Support", "url": "#", "new_window": True},
        {"model": "auth.user"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "catalog.CoinType": "fas fa-coins",
        "orders.Order": "fas fa-shopping-cart",
        "payments.Payment": "fas fa-money-bill-wave",
        "accounts.StaffProfile": "fas fa-id-badge",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True