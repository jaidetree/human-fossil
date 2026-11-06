from adminsortable2.admin import SortableAdminMixin, SortableTabularInline
from django.contrib import admin

from .models import (
    AnimationAward,
    Character,
    Event,
    EventPhoto,
    Illustration,
    Image,
    MangaPreviewPage,
    Section,
)
from .ordering import renumber


class DragNewRowsInline(SortableTabularInline):
    """A sortable inline whose *unsaved* rows are drag-sortable too.

    django-admin-sortable2 only drives saved rows (``tr.has_original``): a row
    added via "Add another" has neither the class nor the handle markup, so it
    can't be dragged until it's saved. ``inline_sortable_new.js`` promotes each
    new row on ``formset:added`` so sortable2's existing Sortable picks it up.
    Loaded via ``Media`` so every sortable inline that subclasses this inherits
    it; the listener is global and no-ops outside ``fieldset.sortable``.
    """

    class Media:
        js = ("human_fossil/inline_sortable_new.js",)


class RenumberingSortableAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Base drag-to-reorder changelist for any model with an ``order`` field.

    django-admin-sortable2 inserts a drag handle (``_reorder_``) as the leftmost
    column and strips ``order`` from the change form. ``order`` is left out of
    ``list_display`` so the handle lands on the left. ``get_fields`` re-adds
    ``order`` on the change form so an editor can type a number by hand when
    editing an existing row; new rows are auto-numbered to the end on add, so
    the add form omits ``order``. Subclasses set ``list_display`` etc.
    """

    class Media:
        # Narrow sortable2's 50px-wide drag-handle column.
        css = {"all": ("human_fossil/sortable_admin.css",)}

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj is not None and "order" not in fields:
            fields.append("order")
        return fields

    def _update_order(self, updated_items, extra_model_filters):
        """Apply the dragged span, then renumber the whole collection 1..N.

        sortable2's drag only reindexes the rows between the drag's start and
        end position, so gaps elsewhere (left by deletes or the add-at-end
        default) survive. After the library applies the move, renumber every
        row by its resulting position so the collection stays gapless.
        """
        super()._update_order(updated_items, extra_model_filters)
        field = self.default_order_field
        rows = list(self.model.objects.filter(**extra_model_filters).order_by(field, "pk"))
        renumbered = renumber(rows, field)
        self.model.objects.bulk_update(renumbered, [field])
        return len(renumbered)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location", "is_published")
    list_filter = ("is_published", "date")
    search_fields = ("title", "location")


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "is_published", "created_at")
    list_filter = ("is_published", "event")
    search_fields = ("title", "caption")


@admin.register(Illustration)
class IllustrationAdmin(RenumberingSortableAdmin):
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title",)


@admin.register(MangaPreviewPage)
class MangaPreviewPageAdmin(RenumberingSortableAdmin):
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title",)


@admin.register(Character)
class CharacterAdmin(RenumberingSortableAdmin):
    list_display = ("name", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("name",)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("title", "image", "created_at")
    search_fields = ("title",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "action", "price", "url")
    search_fields = ("key", "title", "content")


@admin.register(AnimationAward)
class AnimationAwardAdmin(RenumberingSortableAdmin):
    list_display = ("title", "year", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title",)
