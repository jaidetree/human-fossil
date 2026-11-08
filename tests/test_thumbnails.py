"""Grid thumbnails are warmed on save and reused by the home page."""

import logging

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from test_characters import make_character
from test_events import make_photo
from test_illustrations import make_illustration
from test_manga_preview_pages import make_page

from human_fossil import thumbnails


def cached_thumbnails() -> set[str]:
    return {str(p) for p in (settings.MEDIA_ROOT / "cache").rglob("*.webp")}


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("make", [make_page, make_illustration, make_photo, make_character])
def test_saving_warms_the_thumbnail_home_reuses(client: Client, make) -> None:
    before = cached_thumbnails()

    make()
    warmed = cached_thumbnails() - before
    client.get(reverse("home"))

    assert len(warmed) == 1
    assert cached_thumbnails() - before == warmed


@pytest.mark.django_db(transaction=True)
def test_warm_failure_does_not_break_save(monkeypatch, caplog) -> None:
    def boom(*args, **kwargs):
        raise OSError("storage down")

    monkeypatch.setattr(thumbnails, "get_thumbnail", boom)

    with caplog.at_level(logging.ERROR):
        illustration = make_illustration()

    assert illustration.pk is not None
    assert "Thumbnail warm-up failed" in caplog.text
