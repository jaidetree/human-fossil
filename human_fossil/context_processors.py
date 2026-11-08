from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from .models import Section, sections_logger


class SectionMap(dict[str, Section]):
    """Sections keyed by ``key``; an unknown key yields a blank Section.

    Misses never raise so a typo or deleted Section can't break a page; under
    DEBUG they log a warning naming the key.
    """

    def __missing__(self, key: str) -> Section:
        if settings.DEBUG:
            sections_logger.warning("Unknown Section %r", key)
        return Section(key=key)


def load_sections() -> SectionMap:
    queryset = Section.objects.prefetch_related("section_images", "section_meta")
    return SectionMap((section.key, section) for section in queryset)


def sections(request: HttpRequest) -> dict[str, Any]:
    """Expose all Sections as ``sections``: one query, and only if a template uses it."""
    return {"sections": SimpleLazyObject(load_sections)}
