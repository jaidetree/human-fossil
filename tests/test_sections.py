"""Section model, template access via ``sections``, admin and seed data."""

import importlib
import logging
from decimal import Decimal

import pytest
from django.apps import apps
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.template import Context, Engine
from django.test import Client, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

from human_fossil.context_processors import sections as sections_processor
from human_fossil.models import Section

LOGGER = "human_fossil.sections"
ALERT = "javascript:alert('Implement this!')"
HOME_ORDER = [
    "hero",
    "characters",
    "animation",
    "manga",
    "manga-callout",
    "illustrations",
    "art-book-callout",
    "events",
    "event-photos",
    "upcoming-events",
    "past-events",
]


def render(source: str) -> str:
    """Render ``source`` with the real ``sections`` context processor."""
    request = RequestFactory().get("/")
    context = Context(sections_processor(request))
    engine = Engine(libraries={"markdownify": "markdownify.templatetags.markdownify"})
    return engine.from_string("{% load markdownify %}" + source).render(context)


def make_section(key="sample", **kwargs) -> Section:
    return Section.objects.create(key=key, **kwargs)


def test_verbose_names_are_title_cased() -> None:
    assert Section._meta.verbose_name == "Section"
    assert Section._meta.verbose_name_plural == "Sections"


def test_key_help_text_shows_template_reference() -> None:
    assert "sections.<key>" in Section._meta.get_field("key").help_text


@pytest.mark.django_db
def test_defaults_and_str() -> None:
    section = make_section()
    section.refresh_from_db()
    assert (section.title, section.subtitle, section.content, section.action, section.url) == (
        "",
        "",
        "",
        "",
        "",
    )
    assert section.price is None
    assert section.created_at and section.updated_at
    assert str(section) == "sample"


@pytest.mark.django_db
def test_updated_at_changes_on_save() -> None:
    section = make_section()
    created = section.updated_at
    section.title = "New"
    section.save()
    assert section.updated_at > created


@pytest.mark.parametrize("key", ["hero", "art_book_callout", "a1", "h"])
def test_valid_keys_pass(key: str) -> None:
    Section(key=key).clean_fields()


@pytest.mark.parametrize("key", ["art-book", "has space", "Hero", "1hero", "_hero", ""])
def test_invalid_keys_are_rejected(key: str) -> None:
    with pytest.raises(ValidationError) as error:
        Section(key=key).clean_fields()
    assert "key" in error.value.message_dict


@pytest.mark.django_db
def test_key_must_be_unique() -> None:
    with pytest.raises(ValidationError):
        Section(key="hero").full_clean()


@pytest.mark.django_db
def test_href_uses_url_when_set() -> None:
    with override_settings(DEBUG=True):
        assert make_section(url="https://example.com/x").href == "https://example.com/x"


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_href_falls_back_to_hash_in_production(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger=LOGGER):
        assert make_section().href == "#"
    assert caplog.records == []


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_href_falls_back_to_alert_and_warns_in_debug(caplog: pytest.LogCaptureFixture) -> None:
    section = make_section("callout_x")
    with caplog.at_level(logging.WARNING, logger=LOGGER):
        assert section.href == ALERT
    assert "callout_x" in caplog.text


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_alert_href_is_safe_inside_an_attribute() -> None:
    html = render('<a href="{{ sections.nope.href }}">x</a>')
    assert "javascript:alert(&#x27;Implement this!&#x27;)" in html


@pytest.mark.django_db
def test_template_reads_fields_and_renders_markdown() -> None:
    make_section(
        "hero_copy",
        title="Fossil",
        subtitle="By Reb",
        content="Hello *there*",
        action="Go",
        price=Decimal("25.99"),
    )
    html = render(
        "{{ sections.hero_copy.title }}|{{ sections.hero_copy.subtitle }}|"
        "{{ sections.hero_copy.action }}|"
        "{{ sections.hero_copy.price }}|{{ sections.hero_copy.content|markdownify }}"
    )
    assert html == "Fossil|By Reb|Go|25.99|<p>Hello <em>there</em></p>"


@pytest.mark.django_db
def test_owner_edit_shows_in_template() -> None:
    section = make_section(title="Before")
    section.title = "After"
    section.save()
    assert render("{{ sections.sample.title }}") == "After"


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_missing_key_renders_empty_and_silent_in_production(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger=LOGGER):
        html = render(
            "[{{ sections.nope.title }}][{{ sections.nope.price }}][{{ sections.nope.href }}]"
        )
    assert html == "[][None][#]"
    assert caplog.records == []


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_missing_key_warns_naming_the_key_in_debug(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger=LOGGER):
        render("{{ sections.typo_key.title }}")
    assert "typo_key" in caplog.text


@pytest.mark.django_db
def test_all_sections_load_in_one_query(django_assert_num_queries) -> None:
    for key in ("a", "b", "c"):
        make_section(key)
    with django_assert_num_queries(1):
        render("{{ sections.a.title }}")
    with django_assert_num_queries(1):
        render(
            "{{ sections.a.title }}{{ sections.b.title }}"
            "{{ sections.c.title }}{{ sections.d.title }}"
        )


@pytest.mark.django_db
def test_sections_are_not_queried_until_used(django_assert_num_queries) -> None:
    with django_assert_num_queries(0):
        sections_processor(RequestFactory().get("/"))


def test_admin_registers_section() -> None:
    assert Section in admin.site._registry


@pytest.mark.django_db
def test_admin_add_creates_section(admin_client: Client) -> None:
    response = admin_client.post(
        reverse("admin:human_fossil_section_add"), {"key": "extra", "title": "Extra"}
    )
    assert response.status_code == 302
    assert Section.objects.get(key="extra").title == "Extra"


@pytest.mark.django_db
def test_admin_form_surfaces_key_error(admin_client: Client) -> None:
    response = admin_client.post(reverse("admin:human_fossil_section_add"), {"key": "bad-key"})
    assert response.status_code == 200
    assert "key" in response.context["adminform"].form.errors
    assert not Section.objects.filter(key="bad-key").exists()


@pytest.mark.django_db
def test_admin_delete_removes_section(admin_client: Client) -> None:
    section = make_section("gone")
    response = admin_client.post(
        reverse("admin:human_fossil_section_delete", args=[section.pk]), {"post": "yes"}
    )
    assert response.status_code == 302
    assert not Section.objects.filter(key="gone").exists()


SEEDED = {
    "hero": ("Project Human Fossil", "Original story, manga, and animation by Reb", ""),
    "characters": ("Characters", "", ""),
    "animation": ("Animation", "Watch Trailer", "Watch now"),
    "manga": ("Manga", "", ""),
    "manga_callout": ("", "", "Buy the Manga"),
    "illustrations": ("Illustrations", "", ""),
    "art_book_callout": ("", "", "Buy the Art Book"),
    "events": ("Events", "", ""),
}


@pytest.mark.django_db
def test_seed_migration_creates_expected_sections() -> None:
    seeded = {s.key: (s.title, s.subtitle, s.action) for s in Section.objects.all()}
    assert seeded == SEEDED
    assert Section.objects.get(key="manga_callout").price == Decimal("25.99")
    assert Section.objects.get(key="art_book_callout").price == Decimal("32.00")
    assert not Section.objects.exclude(url="").exists()


@pytest.mark.django_db
def test_seed_migration_is_idempotent_and_keeps_owner_edits() -> None:
    Section.objects.filter(key="hero").update(title="Owner title")
    Section.objects.filter(key="events").delete()

    importlib.import_module("human_fossil.migrations.0009_seed_sections").seed(apps, None)

    assert Section.objects.get(key="hero").title == "Owner title"
    assert Section.objects.get(key="events").title == "Events"
    assert Section.objects.count() == len(SEEDED)


@pytest.mark.django_db
def test_home_page_sections_appear_in_specified_order(client: Client) -> None:
    html = client.get(reverse("home")).content.decode()
    positions = [html.index(f'id="{section_id}"') for section_id in HOME_ORDER]
    assert positions == sorted(positions)


@pytest.mark.django_db
def test_home_has_sections_in_context(client: Client) -> None:
    context = client.get(reverse("home")).context
    assert context["sections"]["hero"].title == "Project Human Fossil"


@pytest.mark.django_db
def test_markdownify_keeps_raw_html() -> None:
    make_section("raw_html", content='<div class="x"><span>hi</span><br><h2>T</h2></div>')
    html = render("{{ sections.raw_html.content|markdownify }}")
    assert html == '<div class="x"><span>hi</span><br><h2>T</h2></div>'
