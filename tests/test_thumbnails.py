"""Home grids render sorl thumbnails instead of serving originals."""

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from test_events import make_photo
from test_illustrations import make_illustration
from test_manga_preview_pages import make_page


@pytest.mark.django_db
def test_home_renders_cached_webp_thumbnail_for_each_grid(client: Client) -> None:
    make_page(), make_illustration(), make_photo()
    cache_dir = settings.MEDIA_ROOT / "cache"

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert len(list(cache_dir.rglob("*.webp"))) >= 3
