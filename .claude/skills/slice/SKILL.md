---
name: slice
description: >-
  Use this skill when the user invokes /slice or wants to take one tracked
  vertical slice end-to-end: move it to In Progress, implement it, commit, and
  move it to Review. Trigger on "/slice <issue>", "do slice N", "work issue N",
  or "ship slice N".
---

# Slice

Take one tracked slice of Human Fossil end-to-end: In Progress → implement →
commit → Review.

Requires an issue argument (a `NN-slug` stem or number). Resolve it under
`.human-fossil-vault/Projects/human-fossil/issues/**` by filename stem (zero-pad numbers to
two digits) — the folder it sits in is its current dev state. If no argument, or
the target is ambiguous, stop and ask.

## Steps

1. Read a knowledge summary: `scan-knowledge.sh .human-fossil-vault/Knowledge` (from
   the `knowledge` skill); surface the most relevant points.
2. Read the slice file, plus its spec (`.human-fossil-vault/Projects/human-fossil/Spec.md`),
   `.human-fossil-vault/Domain/CONTEXT.md`, and any `.human-fossil-vault/ADRs` it touches. Stop if the issue isn't
   found — report what failed.
3. Move the slice file (from `Ready` or, if `/afk` dispatched it straight from
   `Backlog`, from `Backlog`) → `In Progress` (folder = dev state; see
   `docs/agents/issue-tracker.md`).
4. `/implement` the slice as specified. Follow project conventions:
   Python 3.13, Django 5.2, `uv`-managed deps; single `human_fossil` app holds all business logic (no `core`/`common`); Tailwind v4 CSS/static assets under Django's `STATICFILES_DIRS`. Write/update tests at the seams the issue names.
5. Verify: `uv run mypy .`, `uv run ruff format --check .`, `uv run ruff check .` and `uv run pytest`. On failure, fix and
   **goto 4**.
6. Commit: `/commit <slice description>`. Skip if nothing to commit; never
   commit partial or failing work.
7. Move the slice file `In Progress` → `Review` — this signals it awaits human
   testing. Check off the acceptance-criteria `- [ ]` boxes that now hold. Only
   a human moves it to `Done`.
8. Run `/knowledge` to record findings — what worked, what broke, and
   non-obvious domain facts — as notes in `.human-fossil-vault/Knowledge/`. Be
   selective.
9. Report a list of manual testing steps for humans.
