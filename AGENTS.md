# Human Fossil

Django 5.2 marketing site.

## Stack

Django 5.2 / Python 3.13 via **uv**, Postgres via `scripts/db`
(Nix-provisioned), Tailwind v4 via CLI, ruff + mypy + pytest. `nix develop`
first; `make help` for targets; `make lint format typecheck test` before done.

Media: Cloudflare R2 via django-storages in prod, falls back to local
`FileSystemStorage` when R2 env vars are unset (local dev, CI). See
`config/settings.py`.

Single app `human_fossil/` holds all business logic; no `core`/`common` app — don't
add one preemptively.

## Sortable-admin pattern

`Work`, `Training`, `Resource` are drag-reorderable in admin via a plain
`order` field. `human_fossil/admin.py`'s `RenumberingSortableAdmin` renumbers the
*entire* collection 1..N after every drag (django-admin-sortable2 alone only
reindexes the dragged span, leaving gaps from deletes/appends) — reuse it for
new sortable models, don't reinvent. Pure renumbering logic lives in
`human_fossil/ordering.py`'s `renumber()`. Ported from `~/projects/gracie`'s
`portfolio` app.

## Agent skills

Docs at `docs/agents/`: vault (`.human-fossil-vault/`), issue tracker
(`.human-fossil-vault/Projects/<slug>/`), triage labels (frontmatter `tags:`),
domain docs (`CONTEXT.md` + ADRs at `.human-fossil-vault/ADRs`).
