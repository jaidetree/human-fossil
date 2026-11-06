"""Test settings: in-memory SQLite and throwaway local file storage.

Overrides whatever DATABASE_URL / R2_* the shell exports, so tests never touch
the real database or bucket.
"""

import tempfile
from pathlib import Path

from .settings import *  # noqa: F403

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}

MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="human_fossil_test_media_"))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Plain static storage: no collectstatic manifest needed to render templates.
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
