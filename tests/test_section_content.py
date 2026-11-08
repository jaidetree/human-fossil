"""Section images and meta: inline models read from templates."""

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from test_events import PNG
from test_sections import make_section, render

from human_fossil.admin import SectionAdmin
from human_fossil.models import Section, SectionImage, SectionMeta


def make_image(section: Section, title="Pic", order=0) -> SectionImage:
    upload = SimpleUploadedFile("Pic.PNG", PNG, content_type="image/png")
    return SectionImage.objects.create(section=section, title=title, image=upload, order=order)


def test_section_admin_inlines_images_and_meta() -> None:
    inlines = {inline.model for inline in SectionAdmin(Section, admin.site).inlines}
    assert inlines == {SectionImage, SectionMeta}


@pytest.mark.django_db
def test_image_upload_path_uses_section_key() -> None:
    name = make_image(make_section("creator")).image.name
    assert name is not None
    assert name.startswith("section_images/creator-")
    assert name.endswith(".png")


@pytest.mark.django_db
def test_images_are_indexable_and_ordered() -> None:
    section = make_section("creator")
    second = make_image(section, "Second", order=2)
    first = make_image(section, "First", order=1)
    assert section.images == [first, second]
    html = render("{{ sections.creator.images.0.title }}|{{ sections.creator.images.1.title }}")
    assert html == "First|Second"


@pytest.mark.django_db
def test_image_url_renders() -> None:
    image = make_image(make_section("creator"))
    assert render("{{ sections.creator.images.0.image.url }}") == image.image.url


@pytest.mark.django_db
def test_missing_image_index_renders_empty() -> None:
    make_section("creator")
    assert render("[{{ sections.creator.images.0.image.url }}]") == "[]"


@pytest.mark.django_db
def test_meta_reads_by_name() -> None:
    section = make_section("my_section")
    SectionMeta.objects.create(section=section, name="subtitle", value="Line 1\nLine 2")
    assert render("{{ sections.my_section.meta.subtitle }}") == "Line 1\nLine 2"


@pytest.mark.django_db
def test_missing_meta_and_unknown_section_render_empty() -> None:
    make_section("my_section")
    html = render("[{{ sections.my_section.meta.nope }}][{{ sections.ghost.meta.x }}]")
    assert html == "[][]"
    assert Section(key="ghost").images == []


@pytest.mark.parametrize("name", ["subtitle", "tag_line", "a1"])
def test_valid_meta_names_pass(name: str) -> None:
    SectionMeta(name=name).clean_fields(exclude=["section"])


@pytest.mark.parametrize("name", ["tag-line", "has space", "Title", "1x", "_x", ""])
def test_invalid_meta_names_are_rejected(name: str) -> None:
    with pytest.raises(ValidationError) as error:
        SectionMeta(name=name).clean_fields(exclude=["section"])
    assert "name" in error.value.message_dict


@pytest.mark.django_db
def test_meta_name_unique_per_section() -> None:
    section = make_section("a")
    SectionMeta.objects.create(section=section, name="x")
    with pytest.raises(ValidationError):
        SectionMeta(section=section, name="x").validate_constraints()
    SectionMeta(section=make_section("b"), name="x").validate_constraints()


@pytest.mark.django_db
def test_deleting_section_cascades() -> None:
    section = make_section("gone")
    make_image(section)
    SectionMeta.objects.create(section=section, name="x")
    section.delete()
    assert not SectionImage.objects.exists()
    assert not SectionMeta.objects.exists()


@pytest.mark.django_db
def test_images_and_meta_add_two_queries_total(django_assert_num_queries) -> None:
    for key in ("a", "b"):
        section = make_section(key)
        make_image(section)
        SectionMeta.objects.create(section=section, name="x", value="v")
    with django_assert_num_queries(3):
        render(
            "{{ sections.a.images.0.title }}{{ sections.b.images.0.title }}"
            "{{ sections.a.meta.x }}{{ sections.b.meta.x }}"
        )
