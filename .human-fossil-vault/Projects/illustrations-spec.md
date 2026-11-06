# Illustrations Spec

Add an `Illustration` model: owner-created images from the manga/animation art
book, shown in their own section on the one-page site, in admin-defined order.

Vocabulary per [[CONTEXT]] (**Illustration**, **Published**).

## Decisions

- Title is required; doubles as image alt text.
- Upload path `illustrations/<slugified title><ext>`, same scheme as
  `EventPhoto`. Same-title collisions get Django storage's random suffix. The
  id isn't usable: `upload_to` runs before the first INSERT, so `pk` is `None`.
- Display names: singular "Illustration", plural "Illustrations" (Django
  default).
- Reuse `RenumberingSortableAdmin` and `renumber()` unchanged.
- Everything loads on the home page (one-pager). Bare-bones markup; owner styles
  it later.

## Model `Illustration` (`human_fossil/models.py`)

| Field          | Type                    | Notes                                         |
| -------------- | ----------------------- | --------------------------------------------- |
| `title`        | `CharField(255)`        | Required                                      |
| `image`        | `ImageField`            | `upload_to` → `illustrations/<slug(title)>.ext` |
| `is_published` | `BooleanField`          | Default `True`                                |
| `order`        | `PositiveIntegerField`  | Default 0; `Meta.ordering = ["order"]`        |
| `created_at`   | `DateTimeField`         | `auto_now_add`                                |
| `updated_at`   | `DateTimeField`         | `auto_now`                                    |

`__str__` returns the title. Includes a migration.

## Admin (`human_fossil/admin.py`)

- Register with `RenumberingSortableAdmin`.
- Drag handle column; `list_display = (title, is_published, created_at)`,
  `list_filter = (is_published,)`, `search_fields = (title,)`.
- Add form omits `order`; new rows auto-numbered to the end. Change form shows
  `order` as a typeable number.

## Page

- `home` view adds `illustrations`: published only, ordered by `order`.
- `templates/home.html`: bare "Illustrations" section, plain image grid,
  `alt=title`, no captions. Section omitted when empty.

## Tests

- Model: defaults (`is_published`), upload path, `__str__`, ordering by `order`.
- Admin: registered; `order` hidden on add, shown on edit.
- View: only published Illustrations in context, in `order`.
- No duplicated assertions.

## Workflow

- Check for `spec.md` before coding; log changes there if present.
- One commit, 50/70 format, includes tests.

## Log

- 2026-11-06: Implemented. Added an extra admin test: new entries append to the
  end (1..N). `tests/test_media_storage.py::test_configures_r2_backend_when_env_vars_present`
  fails on a clean tree too (unrelated; `custom_domain` set to
  `media.humanfossil.com`).
