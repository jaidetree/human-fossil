"""Smoke tests for the empty-but-real Django scaffold.

No CMS content/pages exist yet (see ticket 10) — these just prove the
project boots, the root URL responds, and Django's own system checks pass.
"""

import pytest
from django.core.management import call_command
from django.test import Client


@pytest.mark.django_db
def test_root_returns_200(client: Client) -> None:
    response = client.get("/")
    assert response.status_code == 200


def test_django_check_passes() -> None:
    """`manage.py check` raises SystemExit(0) on success, nothing on failure state."""
    call_command("check")
