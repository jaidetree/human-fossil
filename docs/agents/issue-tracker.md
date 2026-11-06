# Issue tracker: Obsidian project vault

Issues and PRDs live as markdown in the vault at `.human-fossil-vault/Projects/<slug>/`. A visual kanban board (Obsidian Bases `.base` file) renders them for humans; agents operate on the files directly.

## Conventions

- One feature/PRD per dir: `.human-fossil-vault/Projects/<slug>/`. Create with `./new-project.sh <slug>` (from the `setup-project-vault` skill folder).
- PRD/spec: `.human-fossil-vault/Projects/<slug>/Spec.md`.
- Issues/slices: `.human-fossil-vault/Projects/<slug>/issues/<Status>/<NN>-<slug>.md`.
- **Dev state = the folder** the file sits in: `Backlog / Ready / In Progress / Review / Done / Archived`. Moving the file between these folders is the status change.
- **Triage role = frontmatter `tags:`** (e.g. `ready-for-agent`) — see `triage-labels.md`. Orthogonal to dev state.
- **id = the filename** `NN-slug` (e.g. `03-setup-e2e-harness.md`), numbered from `01`.
- **Blocking** (frontmatter, wayfinder-ready): `blocked_by` / `blocks` are lists of relative markdown links to the issue files, e.g. `[02-api](<../Ready/02-api.md>)` (frontmatter-links plugin). **Resolve by filename stem, never the folder segment** — files move between folders, so the path in the link goes stale by design.
- **type** (frontmatter): `research | prototype | grilling | task`.

Issue body template: `.human-fossil-vault/Templates/Issue Template.md` (Description / User Stories / Implementation Plan Overview / Acceptance Criteria).

## When a skill says "publish an issue"

Create a new file in `.human-fossil-vault/Projects/<slug>/issues/Backlog/` with a `ready-for-agent` tag (or the role instructed).

## When a skill says "fetch the relevant ticket"

Find the file by its `NN-slug` stem anywhere under `.human-fossil-vault/Projects/<slug>/issues/` (its folder = current dev state). The user usually passes the number or stem.

## When a skill sets a triage state

Edit the `tags:` frontmatter only. Do **not** move the file between folders — dev state and triage role are independent.

## Dev-state transitions

Driven by `/slice` (which wraps `/implement`), not by triage:

- **Claim / start work**: move `Ready` → `In Progress`.
- **Finish**: move `In Progress` → `Review`. Only a human moves `Review` → `Done`.

## Wayfinding operations

`/wayfinder` uses this tracker as follows:

- **Map** = the project's `Map.md` (`.human-fossil-vault/Projects/<slug>/Map.md`), tagged
  `wayfinder-map` in frontmatter. Its body holds the Destination / Notes /
  Decisions so far / Not yet specified / Out of scope sections. One map per
  project dir. Distinct from `Spec.md` (the PRD/spec) — a project may have a
  map without a spec (spec not written yet) or a spec without a map (no
  wayfinding needed).
- **Ticket** = a normal issue file under `.human-fossil-vault/Projects/<slug>/issues/`,
  using the existing `type:` frontmatter (`research | prototype | grilling |
  task` — these are exactly the wayfinder ticket types) and a `## Question`
  body instead of the Issue Template's Description/User Stories sections.
- **Blocking/frontier**: unchanged from the general convention above —
  `blocked_by`/`blocks` frontmatter, resolved by filename stem. An unblocked
  ticket sits in `Ready/`; a ticket blocked on another sits in `Backlog/`
  until every `blocked_by` stem resolves to a file in `Done/`. The frontier
  is the set of open, unblocked, unclaimed tickets in `Ready/` — "unclaimed"
  meaning no assignee convention is used here, so treat any open `Ready/`
  ticket as claimable.
- **Resolving a ticket**: append the resolution under the ticket's `##
  Question` as a `## Resolution` section, move the file to `Done/`, and add
  a one-line pointer under the map's Decisions so far.
