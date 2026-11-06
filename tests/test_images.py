"""Image model: owner-uploaded files whose URLs get pasted into text.

Provided to the home view but deliberately never rendered by the template.
"""

import pytest
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from test_events import PNG

from human_fossil.admin import RenumberingSortableAdmin
from human_fossil.models import Image


def make_image(title="Logo", **kwargs) -> Image:
    image = SimpleUploadedFile("Logo.PNG", PNG, content_type="image/png")
    return Image.objects.create(title=title, image=image, **kwargs)


@pytest.mark.django_db
def test_str_and_timestamps() -> None:
    image = make_image()
    assert image.created_at and image.updated_at
    assert str(image) == "Logo"


@pytest.mark.django_db
def test_updated_at_changes_on_save() -> None:
    image = make_image()
    created = image.updated_at
    image.title = "Logo 2"
    image.save()
    assert image.updated_at > created


def test_verbose_names_are_title_cased() -> None:
    assert Image._meta.verbose_name == "Image"
    assert Image._meta.verbose_name_plural == "Images"


@pytest.mark.django_db
def test_upload_path_is_slug_plus_random_suffix_and_lowercase_ext() -> None:
    name = make_image(title="Dr. Ada #1!").image.name
    assert name is not None
    assert name.startswith("images/dr-ada-1-")
    assert name.endswith(".png")


@pytest.mark.django_db
def test_same_title_gets_distinct_paths() -> None:
    assert make_image().image.name != make_image().image.name


@pytest.mark.django_db
def test_default_ordering_is_newest_first() -> None:
    older = make_image(title="Older")
    newer = make_image(title="Newer")
    assert list(Image.objects.all()) == [newer, older]


def test_admin_is_plain_not_sortable() -> None:
    model_admin = admin.site._registry[Image]
    assert not isinstance(model_admin, RenumberingSortableAdmin)
    assert "order" not in [f.name for f in Image._meta.fields]
    assert "is_published" not in [f.name for f in Image._meta.fields]


@pytest.mark.django_db
def test_home_context_has_all_images_newest_first(client: Client) -> None:
    older = make_image(title="Older")
    newer = make_image(title="Newer")

    context = client.get(reverse("home")).context

    assert list(context["images"]) == [newer, older]


@pytest.mark.django_db
def test_home_does_not_render_images(client: Client) -> None:
    image = make_image(title="Secret Logo")

    html = client.get(reverse("home")).content.decode()

    assert image.image.url not in html
    assert "Secret Logo" not in html
