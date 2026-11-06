import os

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify


def event_photo_upload_to(instance: "EventPhoto", filename: str) -> str:
    """Store as ``event_photos/<slugified title><ext>``."""
    ext = os.path.splitext(filename)[1].lower()
    return f"event_photos/{slugify(instance.title)}{ext}"


def illustration_upload_to(instance: "Illustration", filename: str) -> str:
    """Store as ``illustrations/<slugified title><ext>``."""
    ext = os.path.splitext(filename)[1].lower()
    return f"illustrations/{slugify(instance.title)}{ext}"


def manga_preview_page_upload_to(instance: "MangaPreviewPage", filename: str) -> str:
    """Store as ``manga_preview_pages/<slugified title><ext>``."""
    ext = os.path.splitext(filename)[1].lower()
    return f"manga_preview_pages/{slugify(instance.title)}{ext}"


def character_upload_to(instance: "Character", filename: str) -> str:
    """Store as ``characters/<slugified name><ext>``."""
    ext = os.path.splitext(filename)[1].lower()
    return f"characters/{slugify(instance.name)}{ext}"


def image_upload_to(instance: "Image", filename: str) -> str:
    """Store as ``images/<slugified title>-<random><ext>``.

    The random suffix keeps URLs unguessable and unique per upload, since the
    owner pastes them into text elsewhere.
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"images/{slugify(instance.title)}-{get_random_string(8)}{ext}"


class Event(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]

    def __str__(self) -> str:
        return self.title


class EventPhoto(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=event_photo_upload_to)
    caption = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    event = models.ForeignKey(
        Event,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="photos",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Booth Photo"
        verbose_name_plural = "Event Booth Photos"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class Illustration(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=illustration_upload_to)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.title


class MangaPreviewPage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=manga_preview_page_upload_to)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Manga Preview Page"
        verbose_name_plural = "Manga Preview Pages"
        ordering = ["order"]

    def __str__(self) -> str:
        return self.title


class Character(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=character_upload_to)
    description = models.TextField(blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Character"
        verbose_name_plural = "Characters"
        ordering = ["order"]

    def __str__(self) -> str:
        return self.name


class Image(models.Model):
    """General-purpose upload; the title doubles as alt text."""

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to=image_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
