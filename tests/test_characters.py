"""Character model, sortable admin and its place on the home view."""

import io

import pytest
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from PIL import Image
from test_events import PNG

from human_fossil.admin import CharacterAdmin, RenumberingSortableAdmin
from human_fossil.models import Character


def make_character(name="Ada", **kwargs) -> Character:
    image = SimpleUploadedFile("Portrait.PNG", PNG, content_type="image/png")
    return Character.objects.create(name=name, image=image, **kwargs)


@pytest.mark.django_db
def test_defaults_and_str() -> None:
    character = make_character()
    assert character.is_published is True
    assert character.description == ""
    assert character.age is None
    assert character.created_at and character.updated_at
    assert str(character) == "Ada"


@pytest.mark.django_db
def test_description_and_age_are_stored() -> None:
    character = make_character(description="Digs things up.", age=34)
    character.refresh_from_db()
    assert (character.description, character.age) == ("Digs things up.", 34)


@pytest.mark.django_db
def test_updated_at_changes_on_save() -> None:
    character = make_character()
    created = character.updated_at
    character.name = "Ada L."
    character.save()
    assert character.updated_at > created


def test_verbose_names_are_title_cased() -> None:
    assert Character._meta.verbose_name == "Character"
    assert Character._meta.verbose_name_plural == "Characters"


@pytest.mark.django_db
def test_upload_path_uses_slugified_name_and_lowercase_ext() -> None:
    assert make_character(name="Dr. Ada #1!").image.name == "characters/dr-ada-1.png"


@pytest.mark.django_db
def test_default_ordering_follows_order_field() -> None:
    second = make_character(name="B", order=2)
    first = make_character(name="A", order=1)
    assert list(Character.objects.all()) == [first, second]


def test_admin_uses_renumbering_sortable_admin() -> None:
    assert isinstance(admin.site._registry[Character], RenumberingSortableAdmin)
    assert CharacterAdmin.list_display[0] == "name"


@pytest.mark.django_db
def test_admin_add_form_hides_order_and_change_form_shows_it(admin_client: Client) -> None:
    add = admin_client.get(reverse("admin:human_fossil_character_add"))
    assert "order" not in add.context["adminform"].form.fields

    obj = make_character()
    change = admin_client.get(reverse("admin:human_fossil_character_change", args=[obj.pk]))
    assert "order" in change.context["adminform"].form.fields


@pytest.mark.django_db
def test_admin_add_numbers_new_entries_to_the_end(admin_client: Client) -> None:
    def upload() -> SimpleUploadedFile:
        buffer = io.BytesIO()
        Image.new("RGB", (2, 2)).save(buffer, "PNG")
        return SimpleUploadedFile("x.png", buffer.getvalue(), content_type="image/png")

    for name in ("a", "b", "c"):
        admin_client.post(
            reverse("admin:human_fossil_character_add"), {"name": name, "image": upload()}
        )

    assert list(Character.objects.values_list("name", "order")) == [
        ("a", 1),
        ("b", 2),
        ("c", 3),
    ]


@pytest.mark.django_db
def test_home_lists_only_published_characters_in_order(client: Client) -> None:
    later = make_character(name="Later", order=2)
    sooner = make_character(name="Sooner", order=1)
    make_character(name="Hidden", order=3, is_published=False)

    context = client.get(reverse("home")).context

    assert list(context["characters"]) == [sooner, later]


@pytest.mark.django_db
def test_home_renders_characters_section_above_manga_even_when_empty(client: Client) -> None:
    html = client.get(reverse("home")).content.decode()
    assert 0 < html.index('id="characters"') < html.index('id="manga"')
