"""Media storage wiring (ticket 16): R2 (S3-compatible, via django-storages)
when R2_* env vars are set, falling back to local FileSystemStorage otherwise.

No real R2 credentials or network calls are used here — the fallback case is
tested by reloading config.settings with the R2 env vars absent (the sandbox
default), and the R2 case is tested with fake-but-well-formed credentials
against moto's mocked S3-compatible backend, never a real bucket.
"""

import importlib

import boto3
import pytest
from moto import mock_aws

import config.settings as settings_module


@pytest.fixture
def reload_settings(monkeypatch: pytest.MonkeyPatch):
    """Reload config.settings under patched env vars, then reload again
    without them so later tests see the sandbox-default (no R2) settings
    module. This only touches the plain settings module object, not
    django.conf.settings — it exercises the same conditional wiring logic
    without mutating already-configured global Django state.
    """

    def _reload():
        return importlib.reload(settings_module)

    yield _reload
    importlib.reload(settings_module)


def test_falls_back_to_filesystem_storage_when_r2_env_vars_absent(
    monkeypatch: pytest.MonkeyPatch, reload_settings
) -> None:
    for var in ("R2_BUCKET_NAME", "R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        monkeypatch.delenv(var, raising=False)

    reloaded = reload_settings()

    assert reloaded.STORAGES["default"]["BACKEND"] == "django.core.files.storage.FileSystemStorage"


def test_configures_r2_backend_when_env_vars_present(
    monkeypatch: pytest.MonkeyPatch, reload_settings
) -> None:
    monkeypatch.setenv("R2_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("R2_ENDPOINT_URL", "https://fake-account.r2.cloudflarestorage.com")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "fake-access-key")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "fake-secret-key")

    reloaded = reload_settings()

    default_storage_config = reloaded.STORAGES["default"]
    assert default_storage_config["BACKEND"] == "storages.backends.s3.S3Storage"

    options = default_storage_config["OPTIONS"]
    assert options["bucket_name"] == "test-bucket"
    assert options["endpoint_url"] == "https://fake-account.r2.cloudflarestorage.com"
    assert options["access_key"] == "fake-access-key"
    assert options["secret_key"] == "fake-secret-key"
    assert options["region_name"] == "auto"
    assert options["custom_domain"] is None


def test_r2_media_urls_use_custom_domain_when_set(
    monkeypatch: pytest.MonkeyPatch, reload_settings
) -> None:
    monkeypatch.setenv("R2_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("R2_ENDPOINT_URL", "https://fake-account.r2.cloudflarestorage.com")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "fake-access-key")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "fake-secret-key")
    monkeypatch.setenv("R2_CUSTOM_DOMAIN", "media.humanfossil.com")

    from storages.backends.s3 import S3Storage

    options = reload_settings().STORAGES["default"]["OPTIONS"]

    assert S3Storage(**options).url("works/a.jpg") == "https://media.humanfossil.com/works/a.jpg"


def test_csrf_trusted_origins_read_from_env(
    monkeypatch: pytest.MonkeyPatch, reload_settings
) -> None:
    monkeypatch.setenv(
        "CSRF_TRUSTED_ORIGINS", "https://humanfossil.com,https://www.humanfossil.com"
    )

    assert reload_settings().CSRF_TRUSTED_ORIGINS == [
        "https://humanfossil.com",
        "https://www.humanfossil.com",
    ]


def test_staticfiles_backend_stays_on_whitenoise_when_r2_configured(
    monkeypatch: pytest.MonkeyPatch, reload_settings
) -> None:
    monkeypatch.setenv("R2_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("R2_ENDPOINT_URL", "https://fake-account.r2.cloudflarestorage.com")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "fake-access-key")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "fake-secret-key")

    reloaded = reload_settings()

    assert (
        reloaded.STORAGES["staticfiles"]["BACKEND"]
        == "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )


@mock_aws
def test_r2_configured_storage_round_trips_a_file_against_mocked_s3() -> None:
    """Prove the constructed S3Storage actually saves to and reads back from
    an S3-compatible backend, using moto's in-memory mock — never a real R2
    bucket or network call. Standing in for a real R2 endpoint, since moto
    mocks boto3's S3 client regardless of the endpoint_url passed to it.
    """
    from django.core.files.base import ContentFile
    from storages.backends.s3 import S3Storage

    bucket_name = "test-bucket"
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket=bucket_name)

    storage = S3Storage(
        bucket_name=bucket_name,
        access_key="fake-access-key",
        secret_key="fake-secret-key",
        region_name="us-east-1",
        querystring_auth=False,
        file_overwrite=False,
    )

    saved_name = storage.save("uploads/example.txt", ContentFile(b"human fossil"))

    assert storage.exists(saved_name)
    with storage.open(saved_name) as saved_file:
        assert saved_file.read() == b"human fossil"
