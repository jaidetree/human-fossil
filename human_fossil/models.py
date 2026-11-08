import logging
import os

from django.conf import settings
from django.core.validators import FileExtensionValidator, RegexValidator
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


def animation_award_upload_to(instance: "AnimationAward", filename: str) -> str:
    """Store as ``animation_awards/<slugified title><ext>``."""
    ext = os.path.splitext(filename)[1].lower()
    return f"animation_awards/{slugify(instance.title)}{ext}"


def section_image_upload_to(instance: "SectionImage", filename: str) -> str:
    """Store as ``section_images/<section key>-<random><ext>``."""
    ext = os.path.splitext(filename)[1].lower()
    return f"section_images/{instance.section.key}-{get_random_string(8)}{ext}"


sections_logger = logging.getLogger("human_fossil.sections")

# Keys double as template variable names (``sections.<key>``): no hyphens.
section_key_validator = RegexValidator(
    r"^[a-z][a-z0-9_]*\Z",
    "Use a lowercase letter first, then lowercase letters, digits and underscores.",
)


class Event(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)
    booth_number = models.CharField(max_length=50, blank=True)
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


class Section(models.Model):
    """Owner-editable content, referenced from templates as ``sections.<key>``.

    A superset of columns; each Section fills the subset it needs. A Section
    with an ``action`` (and usually ``url``/``price``) is a Callout.
    """

    key = models.CharField(
        max_length=64,
        unique=True,
        validators=[section_key_validator],
        help_text="Referenced as `sections.<key>` in templates.",
    )
    title = models.CharField(max_length=255, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True, help_text="Markdown.")
    action = models.CharField(max_length=255, blank=True, help_text="Button label.")
    url = models.URLField(max_length=500, blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="USD."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ["key"]

    def __str__(self) -> str:
        return self.key

    @property
    def href(self) -> str:
        """``url``, else a placeholder that keeps the gap visible.

        ``#`` in production; under DEBUG a JS alert, plus a logged warning.
        """
        if self.url:
            return self.url
        if not settings.DEBUG:
            return "#"
        sections_logger.warning("Section %r has no url", self.key)
        return "javascript:alert('Implement this!')"

    @property
    def images(self) -> list["SectionImage"]:
        """Ordered images, so templates can index: ``sections.<key>.images.0``."""
        if self.pk is None:
            return []
        return list(self.section_images.all())

    @property
    def meta(self) -> dict[str, str]:
        """Name -> value, so templates can read ``sections.<key>.meta.<name>``."""
        if self.pk is None:
            return {}
        return {entry.name: entry.value for entry in self.section_meta.all()}


class SectionImage(models.Model):
    """Image attached to a Section; the title doubles as alt text."""

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="section_images")
    title = models.CharField(max_length=255, blank=True, help_text="Alt text.")
    image = models.ImageField(upload_to=section_image_upload_to)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        verbose_name = "Section Image"
        verbose_name_plural = "Section Images"
        ordering = ["order", "pk"]

    def __str__(self) -> str:
        return self.title or str(self.image)


class SectionMeta(models.Model):
    """Free-form named value on a Section: ``sections.<key>.meta.<name>``."""

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="section_meta")
    name = models.CharField(
        max_length=64,
        validators=[section_key_validator],
        help_text="Referenced as `meta.<name>` in templates.",
    )
    value = models.TextField(blank=True)

    class Meta:
        verbose_name = "Section Meta"
        verbose_name_plural = "Section Meta"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["section", "name"], name="unique_section_meta_name")
        ]

    def __str__(self) -> str:
        return self.name


class AnimationAward(models.Model):
    title = models.CharField(max_length=255)
    award = models.CharField(max_length=255, blank=True, help_text='e.g. "Award Winner"')
    category = models.CharField(max_length=255, blank=True, help_text='e.g. "Best Picture"')
    year = models.PositiveSmallIntegerField()
    # FileField, not ImageField: ImageField rejects SVG.
    icon = models.FileField(
        upload_to=animation_award_upload_to,
        validators=[FileExtensionValidator(["png", "svg", "webp"])],
        blank=True,
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Animation Award"
        verbose_name_plural = "Animation Awards"
        ordering = ["order"]

    def __str__(self) -> str:
        return self.title
