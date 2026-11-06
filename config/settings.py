"""
Django settings for the Human Fossil project.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-local-dev-only-do-not-use-in-production",
)

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "adminsortable2",
    "markdownify",
    "human_fossil",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
                "human_fossil.context_processors.sections",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database — local dev/CI point DATABASE_URL at the Nix-provisioned local
# Postgres started by scripts/db; production points it at Crunchy Bridge.
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://localhost:5432/human_fossil_dev",
    ),
}

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files — WhiteNoise serves STATIC_ROOT (collectstatic output) at
# runtime; STATICFILES_DIRS is where the Tailwind CLI build (see
# static_src/css/input.css -> static/css/app.css) and other pre-built assets
# live before collectstatic bakes them into STATIC_ROOT at image build time.
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES: dict[str, dict[str, object]] = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media — owner-uploaded Work/WorkImage/Training/Resource files. Routed
# through Cloudflare R2 (S3-compatible, via django-storages) when the R2
# env vars below are set; falls back to local filesystem storage (the
# STORAGES["default"] set above) when they are not, which is the case in
# local dev and CI. Individual model fields never set storage= directly —
# they all pick up whichever backend STORAGES["default"] resolves to.
#
# Required env vars for R2 (set as Fly secrets in production — see ticket
# 18, production cutover):
#   R2_BUCKET_NAME       — the R2 bucket name
#   R2_ENDPOINT_URL       — R2 S3-compatible endpoint, e.g.
#                           https://<account_id>.r2.cloudflarestorage.com
#   R2_ACCESS_KEY_ID      — R2 API token access key
#   R2_SECRET_ACCESS_KEY  — R2 API token secret key
# Optional:
#   R2_CUSTOM_DOMAIN      — public hostname bound to the bucket, e.g.
#                           media.humanfossil.com (no scheme). Media URLs are
#                           built from it; without it they'd point at the
#                           authenticated S3 API endpoint and not load.
# All four required vars must be set for R2 storage to activate; if any/all are absent,
# Django falls back to FileSystemStorage under MEDIA_ROOT.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

R2_BUCKET_NAME = env("R2_BUCKET_NAME", default=None)
if R2_BUCKET_NAME:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": R2_BUCKET_NAME,
            "endpoint_url": env("R2_ENDPOINT_URL"),
            "access_key": env("R2_ACCESS_KEY_ID"),
            "secret_key": env("R2_SECRET_ACCESS_KEY"),
            # R2 has no region concept but boto3 requires one; "auto" is
            # R2's documented value.
            "region_name": "auto",
            # R2 doesn't support the ACL query param S3 uses by default.
            "default_acl": None,
            "custom_domain": env("R2_CUSTOM_DOMAIN", default=None),
            "querystring_auth": False,
            "file_overwrite": False,
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-markdownify — renders `human_fossil` app Markdown fields (Work.description,
# WorkImage.caption, ...) via the `|markdownify` template filter. A restrictive
# allowed-tags whitelist: enough for prose (paragraphs, emphasis, links, lists)
# with no raw HTML/script/embed surface for owner-authored content.
MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": [
            "a",
            "b",
            "blockquote",
            "em",
            "i",
            "li",
            "ol",
            "p",
            "strong",
            "ul",
        ],
        "WHITELIST_ATTRS": ["href", "title"],
        "WHITELIST_PROTOCOLS": ["http", "https", "mailto"],
    },
}
