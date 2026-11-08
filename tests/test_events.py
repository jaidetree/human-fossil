"""Event / EventPhoto models, admin registration and the home view."""

import datetime

import pytest
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from human_fossil.models import Event, EventPhoto

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDA"
    b"Tx\x9cc````\x00\x00\x00\x05\x00\x01\xa5\xf6E@\x00\x00\x00\x00IEND\xaeB`\x82"
)


def make_event(days_from_today: int = 0, **kwargs) -> Event:
    date = timezone.localdate() + datetime.timedelta(days=days_from_today)
    defaults = {"title": f"Event {days_from_today}", "date": date, "location": "Somewhere"}
    return Event.objects.create(**{**defaults, **kwargs})


def make_photo(title="Booth Shot", **kwargs) -> EventPhoto:
    image = SimpleUploadedFile("IMG_0001.PNG", PNG, content_type="image/png")
    return EventPhoto.objects.create(title=title, image=image, **kwargs)


@pytest.mark.django_db
def test_models_default_to_published_and_stamp_timestamps() -> None:
    event, photo = make_event(), make_photo()
    for obj in (event, photo):
        assert obj.is_published is True
        assert obj.created_at and obj.updated_at


@pytest.mark.django_db
def test_photo_upload_path_uses_slugified_title_and_lowercase_ext() -> None:
    photo = make_photo(title="Booth Shot #1!")
    assert photo.image.name == "event_photos/booth-shot-1.png"


@pytest.mark.django_db
def test_deleting_event_keeps_photo() -> None:
    event = make_event()
    photo = make_photo(event=event)
    event.delete()
    photo.refresh_from_db()
    assert photo.event is None


@pytest.mark.django_db
def test_photo_caption_and_event_are_optional() -> None:
    photo = make_photo()
    photo.full_clean()
    assert photo.caption == "" and photo.event is None


@pytest.mark.django_db
def test_event_booth_number_is_optional_free_text() -> None:
    plain = make_event()
    plain.full_clean()
    assert plain.booth_number == ""

    prefixed = make_event(booth_number="AA-12b")
    prefixed.full_clean()
    prefixed.refresh_from_db()
    assert prefixed.booth_number == "AA-12b"


def test_verbose_names() -> None:
    assert EventPhoto._meta.verbose_name == "Event Booth Photo"
    assert EventPhoto._meta.verbose_name_plural == "Event Booth Photos"
    assert Event._meta.verbose_name == "event"


def test_models_registered_in_admin() -> None:
    assert Event in admin.site._registry
    assert EventPhoto in admin.site._registry


@pytest.mark.django_db
def test_home_splits_published_events_by_date(client: Client) -> None:
    soon, later = make_event(2), make_event(9)
    recent, old = make_event(-2), make_event(-9)
    today = make_event(0)
    make_event(3, is_published=False)

    context = client.get(reverse("home")).context

    assert list(context["upcoming_events"]) == [today, soon, later]
    assert list(context["past_events"]) == [recent, old]


@pytest.mark.django_db
def test_home_lists_only_published_photos(client: Client) -> None:
    shown = make_photo(title="Shown")
    make_photo(title="Hidden", is_published=False)

    context = client.get(reverse("home")).context

    assert list(context["event_photos"]) == [shown]
