"""AnimationAward model, sortable admin and its place on the home view."""

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from test_events import PNG

from human_fossil.admin import AnimationAwardAdmin, RenumberingSortableAdmin
from human_fossil.models import AnimationAward

SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>'


def make_award(title="Best Short", filename="Badge.PNG", content=PNG, **kwargs) -> AnimationAward:
    icon = SimpleUploadedFile(filename, content, content_type="application/octet-stream")
    return AnimationAward.objects.create(title=title, year=2025, icon=icon, **kwargs)


@pytest.mark.django_db
def test_defaults_and_str() -> None:
    award = make_award()
    assert award.is_published is True
    assert award.created_at and award.updated_at
    assert str(award) == "Best Short"


def test_verbose_names_are_title_cased() -> None:
    assert AnimationAward._meta.verbose_name == "Animation Award"
    assert AnimationAward._meta.verbose_name_plural == "Animation Awards"


@pytest.mark.django_db
def test_upload_path_uses_slugified_title_and_lowercase_ext() -> None:
    assert make_award(title="Gold Reel!").icon.name == "animation_awards/gold-reel.png"


@pytest.mark.django_db
@pytest.mark.parametrize("filename", ["a.png", "a.svg", "a.webp", "a.SVG"])
def test_icon_accepts_png_svg_webp(filename: str) -> None:
    make_award(filename=filename, content=SVG).full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("filename", ["a.gif", "a.jpg", "a.pdf", "a.exe"])
def test_icon_rejects_other_extensions(filename: str) -> None:
    award = make_award(filename=filename)
    with pytest.raises(ValidationError) as error:
        award.full_clean()
    assert "icon" in error.value.message_dict


@pytest.mark.django_db
def test_default_ordering_follows_order_field() -> None:
    second = make_award(title="B", order=2)
    first = make_award(title="A", order=1)
    assert list(AnimationAward.objects.all()) == [first, second]


def test_admin_uses_renumbering_sortable_admin() -> None:
    assert isinstance(admin.site._registry[AnimationAward], RenumberingSortableAdmin)
    assert AnimationAwardAdmin.list_display[0] == "title"


@pytest.mark.django_db
def test_admin_add_form_hides_order_and_change_form_shows_it(admin_client: Client) -> None:
    add = admin_client.get(reverse("admin:human_fossil_animationaward_add"))
    assert "order" not in add.context["adminform"].form.fields

    obj = make_award()
    change = admin_client.get(reverse("admin:human_fossil_animationaward_change", args=[obj.pk]))
    assert "order" in change.context["adminform"].form.fields


@pytest.mark.django_db
def test_admin_add_numbers_new_entries_to_the_end(admin_client: Client) -> None:
    for title in ("a", "b", "c"):
        admin_client.post(
            reverse("admin:human_fossil_animationaward_add"),
            {
                "title": title,
                "year": 2025,
                "icon": SimpleUploadedFile("x.svg", SVG, content_type="image/svg+xml"),
            },
        )

    assert list(AnimationAward.objects.values_list("title", "order")) == [
        ("a", 1),
        ("b", 2),
        ("c", 3),
    ]


@pytest.mark.django_db
def test_home_lists_only_published_awards_in_order(client: Client) -> None:
    later = make_award(title="Later", order=2)
    sooner = make_award(title="Sooner", order=1)
    make_award(title="Hidden", order=3, is_published=False)

    context = client.get(reverse("home")).context

    assert list(context["animation_awards"]) == [sooner, later]


@pytest.mark.django_db
def test_home_renders_awards_list_inside_animation_even_when_empty(client: Client) -> None:
    html = client.get(reverse("home")).content.decode()
    animation = html[html.index('id="animation"') : html.index('id="manga"')]
    assert 'id="animation-awards"' in animation
