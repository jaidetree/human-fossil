"""MangaPreviewPage model, sortable admin and its place on the home view."""

import io

import pytest
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from PIL import Image
from test_events import PNG

from human_fossil.admin import MangaPreviewPageAdmin, RenumberingSortableAdmin
from human_fossil.models import MangaPreviewPage


def make_page(title="Page One", **kwargs) -> MangaPreviewPage:
    image = SimpleUploadedFile("Page_01.PNG", PNG, content_type="image/png")
    return MangaPreviewPage.objects.create(title=title, image=image, **kwargs)


@pytest.mark.django_db
def test_defaults_and_str() -> None:
    page = make_page()
    assert page.is_published is True
    assert page.created_at and page.updated_at
    assert str(page) == "Page One"


@pytest.mark.django_db
def test_upload_path_uses_slugified_title_and_lowercase_ext() -> None:
    assert make_page(title="Page #1!").image.name == "manga_preview_pages/page-1.png"


@pytest.mark.django_db
def test_default_ordering_follows_order_field() -> None:
    second = make_page(title="B", order=2)
    first = make_page(title="A", order=1)
    assert list(MangaPreviewPage.objects.all()) == [first, second]


def test_admin_uses_renumbering_sortable_admin() -> None:
    assert isinstance(admin.site._registry[MangaPreviewPage], RenumberingSortableAdmin)
    assert MangaPreviewPageAdmin.list_display[0] == "title"


@pytest.mark.django_db
def test_admin_add_form_hides_order_and_change_form_shows_it(admin_client: Client) -> None:
    add = admin_client.get(reverse("admin:human_fossil_mangapreviewpage_add"))
    assert "order" not in add.context["adminform"].form.fields

    obj = make_page()
    change = admin_client.get(reverse("admin:human_fossil_mangapreviewpage_change", args=[obj.pk]))
    assert "order" in change.context["adminform"].form.fields


@pytest.mark.django_db
def test_home_lists_only_published_manga_preview_pages_in_order(client: Client) -> None:
    later = make_page(title="Later", order=2)
    sooner = make_page(title="Sooner", order=1)
    make_page(title="Hidden", order=3, is_published=False)

    context = client.get(reverse("home")).context

    assert list(context["manga_preview_pages"]) == [sooner, later]


@pytest.mark.django_db
def test_admin_add_numbers_new_entries_to_the_end(admin_client: Client) -> None:
    def upload() -> SimpleUploadedFile:
        buffer = io.BytesIO()
        Image.new("RGB", (2, 2)).save(buffer, "PNG")
        return SimpleUploadedFile("x.png", buffer.getvalue(), content_type="image/png")

    for title in ("a", "b", "c"):
        admin_client.post(
            reverse("admin:human_fossil_mangapreviewpage_add"), {"title": title, "image": upload()}
        )

    assert list(MangaPreviewPage.objects.values_list("title", "order")) == [
        ("a", 1),
        ("b", 2),
        ("c", 3),
    ]
