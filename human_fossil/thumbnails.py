"""Home grid thumbnails: one definition for templates and the on-save warm-up.

Templates use ``{% grid_thumbnail obj as thumb %}``; saving a model warms the
same thumbnail so visitors never pay the cold hit.
"""

import logging
from typing import Any

from django.db import models, transaction
from sorl.thumbnail import get_thumbnail

from .models import Character, EventPhoto, Illustration, MangaPreviewPage

logger = logging.getLogger(__name__)

GRID_SIZES: dict[type[models.Model], str] = {
    Character: "540x720",
    MangaPreviewPage: "720x1000",
    Illustration: "720x720",
    EventPhoto: "540x982",
}


def grid_thumbnail(instance: Any) -> Any:
    """Thumbnail for ``instance.image`` at its grid size; the original if it fails."""
    size = GRID_SIZES[type(instance)]
    return get_thumbnail(instance.image, size, crop="center", format="WEBP") or instance.image


def warm(instance: Any) -> None:
    """Generate the grid thumbnail; a failure must never break the save."""
    try:
        grid_thumbnail(instance)
    except Exception:
        logger.exception("Thumbnail warm-up failed for %r", instance)


def warm_on_save(sender: type[models.Model], instance: Any, **kwargs: Any) -> None:
    transaction.on_commit(lambda: warm(instance))


def connect() -> None:
    for model in GRID_SIZES:
        models.signals.post_save.connect(
            warm_on_save, sender=model, dispatch_uid=f"warm-thumbnail-{model.__name__}"
        )
