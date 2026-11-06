---
tags:
  - ready-for-agent
---

# Editable Site Content Spec

Let the site owner edit headings, blurbs, callout copy, prices and CTA URLs
from Django admin, and add an Animation Award list. Vocabulary per [[CONTEXT]]
(**Published**); new terms (**Section**, **Callout**, **Animation Award**) are
proposed for the glossary, see Further Notes.

## Problem Statement

The owner of the one-page site can upload images and events, but all copy is
hardcoded in the template: the hero title, subtitle and intro, every section
heading, the calls to action for the trailer, the manga and the art book, and
the events blurb. Changing a word, a price or a buy-link means a developer edit
and a deploy. Awards the animation won have nowhere to live. The owner also
wants to define new editable sections before the developer has written markup
for them, and wants the same content reusable if a second page appears later.

## Solution

Introduce a **Section**: a named, owner-editable content record that templates
reference declaratively, e.g. `sections.hero.title`. The owner edits Sections
in admin, including adding new ones. Missing Sections never break a page: they
render empty, and in development they log a warning. Callouts (trailer, manga,
art book) are Sections with an action label, a URL and optionally a price. A
callout with no URL still renders its button, pointing at a visible
placeholder so the gap is noticed. Awards are a separate sortable, publishable
list rendered inside the animation Section.

## User Stories

1. As the site owner, I want to edit the hero title, subtitle and intro in
   admin, so that I can change the pitch without a developer.
2. As the site owner, I want to write Section content in Markdown, so that I
   can use paragraphs, emphasis, lists and links.
3. As the site owner, I want each section heading to be editable, so that I can
   rename "Characters" or "Manga" myself.
4. As the site owner, I want to edit the animation callout text and button
   label, so that I can point visitors at the trailer or film.
5. As the site owner, I want to set the trailer/film URL once I know where the
   video lives, so that the button works without a deploy.
6. As the site owner, I want to edit the manga callout text, button label,
   price and URL, so that I can change the offer or point it at a shop page.
7. As the site owner, I want to edit the art book callout text, button label,
   price and URL, for the same reason.
8. As the site owner, I want the price stored as its own field rather than in
   the button label, so that the developer can style it separately.
9. As the site owner, I want to edit the events blurb about the booth, so that
   visitors know what to expect there.
10. As the site owner, I want to add a new Section with my own key, so that I
    can write content before the markup exists.
11. As the site owner, I want a clear form error when my key isn't valid for
    templates, so that I don't create a Section that silently never renders.
12. As the site owner, I want the key's help text to show how templates
    reference it, so that I can tell the developer the exact name.
13. As the site owner, I want to delete a Section I no longer need, so that
    admin stays tidy.
14. As the site owner, I want to add Animation Awards with an icon, title and
    year, so that I can showcase what the film won.
15. As the site owner, I want to upload an award icon as PNG, SVG or WebP, so
    that I can use vector badges.
16. As the site owner, I want to drag awards into my preferred order, so that
    the best ones come first.
17. As the site owner, I want to unpublish an award without deleting it, so
    that I can hide it temporarily.
18. As the site owner, I want newly created awards appended to the end of the
    list, so that I don't have to renumber manually.
19. As the site owner, I want a callout with no URL to still show its button,
    visibly pointing at a placeholder, so that I notice it needs fixing
    instead of forgetting it.
20. As a site visitor, I want to read the hero, headings and blurbs, so that I
    understand what the project is.
21. As a site visitor, I want to click the trailer, manga and art book buttons,
    so that I can watch or buy.
22. As a site visitor, I want to see the price near the buy button, so that I
    know what I'm committing to.
23. As a site visitor, I want to see the animation's awards beside the trailer
    callout, so that I trust the quality.
24. As a site visitor, I want the page sections in a sensible order (hero,
    characters, animation, manga, manga callout, illustrations, art book
    callout, events), so that the page tells a story.
25. As a site visitor, I want a missing or half-filled Section never to cause
    an error page, so that the site stays up.
26. As the developer, I want to reference Sections declaratively in templates,
    so that markup stays simple and doesn't need view changes per Section.
27. As the developer, I want a warning logged in development when a template
    references a Section that doesn't exist, so that typos surface early.
28. As the developer, I want that same miss to be silent in production, so that
    visitors and logs aren't affected.
29. As the developer, I want one database query per request for all Sections,
    so that adding references doesn't add queries.
30. As the developer, I want a `href` that falls back to a placeholder, so
    that every button has a safe link target.
31. As the developer, I want the fallback to be an alert in development and
    `#` in production, so that dev builds nag me and production stays inert.
32. As the developer, I want Sections to be reusable on any future page, so
    that I don't duplicate content per page.
33. As the developer, I want the initial Sections seeded by migration without
    overwriting owner edits, so that deploys never clobber production copy.
34. As the developer, I want no new dependencies for Markdown, so that the
    project stays small.
35. As the developer, I want the Upcoming and Past event headings to stay in
    the template, so that structural labels aren't owner-editable.

## Implementation Decisions

### Section

- New model, display names "Section" / "Sections", with timestamps
  (`created_at`, `updated_at`) like the other models.
- `key`: unique; validated at form/model-clean time against lowercase letter
  first, then lowercase letters, digits and underscores. No hyphens, because
  the key must be a valid template variable name. Help text states "Referenced
  as `sections.<key>`".
- `title`: short text, may be blank. Used as the Section's heading.
- `subtitle`: short text, may be blank. Folds in the old "prompt" idea (e.g.
  the animation callout's "Watch Trailer").
- `content`: long text, may be blank, Markdown. Rendered in templates with the
  `markdownify` filter from the already-installed and configured
  django-markdownify. Content is owner-authored and trusted, so no additional
  sanitising layer.
- `action`: short text, may be blank. The button label.
- `url`: URL field, may be blank.
- `price`: nullable decimal. Display in USD only; the template adds the
  currency symbol.
- Unused columns on a row are left blank. Different Sections use different
  subsets.
- `href` (property, usable from templates as a zero-argument lookup): returns
  `url` when set; otherwise a fallback. Fallback is `#` when `DEBUG` is false;
  when `DEBUG` is true it is a JavaScript alert reading "Implement this!" and
  a warning is logged. Autoescaped quotes inside an attribute decode in the
  browser and need no `mark_safe`; verify in a test.
- Admin allows add, edit and delete: Sections are dynamic.

### Template access

- A context processor exposes `sections`, a mapping loaded with one query per
  request (all rows) and keyed by `key`. Templates use dotted lookup, e.g.
  `sections.hero.title`.
- Lookup of an unknown key returns a blank Section stand-in: every field
  renders empty and `href` resolves to the fallback. When `DEBUG` is true the
  miss logs a warning naming the key; in production it is silent.
- Because the processor is global, a future second page can use any Section
  without view changes. Sections are keyed by their own identity, never by
  page.
- Callout markup is **not** wrapped in a conditional on `url`. A blank URL
  intentionally renders a visibly odd button (placeholder `href`) so the owner
  sees the gap.

### Seed data

A data migration creates each Section below if its key doesn't exist
(`get_or_create` semantics, never overwriting). All `url` values are blank.

| key               | title                | subtitle                                      | content                                                                                                                                                                                                                                  | action             | price |
| ----------------- | -------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ----- |
| `hero`            | Project Human Fossil | Original story, manga, and animation by Reb   | A breath taking story about the remnants of civilization trying to survive as their planet runs out of breathable oxygen. Join characters Saesh and Yen on their perilous journey to salvage resources to make life underground better and fight for the future! | —                  | —     |
| `characters`      | Characters           | —                                             | —                                                                                                                                                                                                                                        | —                  | —     |
| `animation`       | Animation            | Watch Trailer                                 | Watch the award winning full animated film now                                                                                                                                                                                           | Watch now          | —     |
| `manga`           | Manga                | —                                             | —                                                                                                                                                                                                                                        | —                  | —     |
| `manga_callout`   | —                    | —                                             | Enjoying the preview? Get your own digital copy to experience the full story and support this project                                                                                                                                    | Buy the Manga      | 25.99 |
| `illustrations`   | Illustrations        | —                                             | —                                                                                                                                                                                                                                        | —                  | —     |
| `art_book_callout`| —                    | —                                             | Enjoy the art? Get the art book and explore the lore.                                                                                                                                                                                    | Buy the Art Book   | 32.00 |
| `events`          | Events               | —                                             | Placeholder booth blurb for the owner to replace                                                                                                                                                                                         | —                  | —     |

Notes: the hero subtitle uses "manga" where the source said "manage" (assumed
typo; owner can edit). The trailer text omits the platform because the video's
location isn't known. There is no separate `event_photos` row: the booth
photos render under the events block without their own heading.

### AnimationAward

- New model, display names "Animation Award" / "Animation Awards".
- Fields: `icon` (file field, extension-restricted to PNG, SVG and WebP; an
  image field is unsuitable because it rejects SVG), `title`, `year`,
  `is_published` (default true), `order` (sortable, same helper as other
  sortable models), plus timestamps.
- Admin reuses the existing sortable/renumbering admin base: drag handle,
  `order` hidden on add (appended to the end) and typeable on edit.
- The `home` view adds `animation_awards`: published only, ordered by `order`.
- Rendered as a bare list inside the `animation` Section, after the callout.
  The list is always rendered, even when empty and regardless of the
  animation `url`.

### Page order (home)

Hero, Characters, Animation (with awards), Manga, Manga Callout,
Illustrations, Art Book Callout, Events (heading and blurb), Event Booth
Photos, then the hardcoded Upcoming and Past event lists. Bare-bones markup,
as elsewhere in the project; the owner styles later. Existing content
sections keep their current queries; only their headings come from Sections.

## Testing Decisions

- A good test exercises external behaviour: what the rendered page shows and
  what admin forms accept or reject, not how the mapping is built internally.
- **Seam**: the Django test client against the `home` URL, plus admin form
  behaviour. This is the highest existing seam and the one used by the other
  model tests in this project. Model-level checks (key validation, `href`) are
  exercised via the same suites without introducing a new seam.
- Cover:
  - Seeded Sections appear on the page with expected headings, subtitle,
    intro (rendered Markdown), button label and price.
  - An owner edit to a Section's title/content shows on the page.
  - A missing key renders empty without error; logs a warning when `DEBUG` is
    true and not when false.
  - Callout with blank `url`: button still renders; `href` is `#` in
    production and the alert in dev; with a URL set, the button uses it.
  - Key validation rejects hyphens, spaces, uppercase and leading digits; the
    admin form surfaces the error.
  - Admin allows add and delete of Sections.
  - Seed migration is idempotent and doesn't overwrite an edited row.
  - AnimationAward: defaults, upload extension validation (accepts PNG, SVG,
    WebP; rejects others), `__str__`, ordering by `order`, admin hides
    `order` on add and shows on edit, new rows append to the end.
  - View: only published awards in context, in order; awards list renders
    within the animation block when none exist.
  - Page section order matches the specified sequence.
  - One query for all Sections per request (assert query count stays flat as
    references increase).
- Prior art: the existing model/admin/home-view tests for Character,
  Illustration and MangaPreviewPage, and the root smoke test. Avoid duplicated
  assertions across them.

## Out of Scope

- Page-builder behaviour: owners can't reorder or place Sections on the page.
- A separate `Link` model or lists of links (socials); single CTA per Section.
- Multiple pages or page models. Sections are reusable but no second page is
  built.
- Editable "Upcoming" / "Past" event headings.
- Multi-currency prices or formatting beyond a USD `$` prefix.
- A WYSIWYG editor or additional Markdown/sanitising dependencies.
- Choosing the platform or URL for the trailer.
- Real events blurb copy (placeholder seeded).
- Styling.

## Further Notes

- Proposed glossary terms for `Domain/CONTEXT.md` (via `/domain-modeling`):
  **Section** (owner-editable content record, referenced by key), **Callout**
  (Section with action label, URL and optional price), **Animation Award**.
- Callouts are deliberately not conditionally hidden when empty, so gaps stay
  visible.
- Open for the owner: the events blurb text, the trailer platform and URL, and
  whether "manage" in the hero subtitle was intentional.
- Workflow reminders: check `spec.md` before coding and log changes there; one
  commit, 50/70 message format, tests included.

## Implementation Log

- Added `Section` and `AnimationAward` models (migration 0008), seed data
  migration 0009 (`get_or_create`, never overwrites), admin for both
  (`AnimationAward` reuses `RenumberingSortableAdmin`).
- `human_fossil.context_processors.sections` exposes a lazy `sections` map: one
  query, none on pages that don't use it (e.g. admin). Unknown key -> blank
  `Section`; warning logged only under `DEBUG`.
- `home` view adds `animation_awards`; `home.html` rewritten to the specified
  order, with Section-driven copy. Awards list (`#animation-awards`) always
  renders. "Event Booth Photos" heading removed per spec.
- Testing: views assert on `response.context` (AGENTS.md); Section rendering
  behaviour is tested by rendering small templates through the real context
  processor; page order via `html.index` (precedent: test_characters).
- Seeded rows exist in the test DB, so Section tests use non-seeded keys.
