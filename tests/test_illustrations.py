"""Illustration model, sortable admin and its place on the home view."""

import io

import pytest
from PIL import Image
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from human_fossil.admin import IllustrationAdmin, RenumberingSortableAdmin
from human_fossil.models import Illustration

from test_events import PNG


def make_illustration(title="Cover Art", **kwargs) -> Illustration:
    image = SimpleUploadedFile("Page_01.PNG", PNG, content_type="image/png")
    return Illustration.objects.create(title=title, image=image, **kwargs)


@pytest.mark.django_db
def test_defaults_and_str() -> None:
    illustration = make_illustration()
    assert illustration.is_published is True
    assert illustration.created_at and illustration.updated_at
    assert str(illustration) == "Cover Art"


@pytest.mark.django_db
def test_upload_path_uses_slugified_title_and_lowercase_ext() -> None:
    assert make_illustration(title="Cover Art #1!").image.name == "illustrations/cover-art-1.png"


@pytest.mark.django_db
def test_default_ordering_follows_order_field() -> None:
    second = make_illustration(title="B", order=2)
    first = make_illustration(title="A", order=1)
    assert list(Illustration.objects.all()) == [first, second]


def test_admin_uses_renumbering_sortable_admin() -> None:
    assert isinstance(admin.site._registry[Illustration], RenumberingSortableAdmin)
    assert IllustrationAdmin.list_display[0] == "title"


@pytest.mark.django_db
def test_admin_add_form_hides_order_and_change_form_shows_it(admin_client: Client) -> None:
    add = admin_client.get(reverse("admin:human_fossil_illustration_add"))
    assert "order" not in add.context["adminform"].form.fields

    obj = make_illustration()
    change = admin_client.get(reverse("admin:human_fossil_illustration_change", args=[obj.pk]))
    assert "order" in change.context["adminform"].form.fields


@pytest.mark.django_db
def test_home_lists_only_published_illustrations_in_order(client: Client) -> None:
    later = make_illustration(title="Later", order=2)
    sooner = make_illustration(title="Sooner", order=1)
    make_illustration(title="Hidden", order=3, is_published=False)

    context = client.get(reverse("home")).context

    assert list(context["illustrations"]) == [sooner, later]


@pytest.mark.django_db
def test_admin_add_numbers_new_entries_to_the_end(admin_client: Client) -> None:
    def upload() -> SimpleUploadedFile:
        buffer = io.BytesIO()
        Image.new("RGB", (2, 2)).save(buffer, "PNG")
        return SimpleUploadedFile("x.png", buffer.getvalue(), content_type="image/png")

    for title in ("a", "b", "c"):
        admin_client.post(
            reverse("admin:human_fossil_illustration_add"), {"title": title, "image": upload()}
        )

    assert list(Illustration.objects.values_list("title", "order")) == [("a", 1), ("b", 2), ("c", 3)]
