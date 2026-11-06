# Human Fossil

One-page site showcasing events, the booth photos taken at them, the
owner's illustrations, and a few manga preview pages.

## Glossary

**Event**
A dated gathering with a title and location. Shown in an *upcoming* section
(date today or later) or a *past* section. Single-day: no end date. Hidden from
the page when unpublished.

**Event Booth Photo**
Photo of the booth, optionally linked to an Event. Model: `EventPhoto`.
Featured in its own section, independent of Events. Survives deletion of its
Event (the link is cleared). Hidden from the page when unpublished.

**Illustration**
Image created by the site owner, from the art book for the manga/animation.
Has a title. Featured in its own section, independent of Events and Booth
Photos. Shown in an admin-defined order. Hidden from the page when unpublished.

**Manga Preview Page**
Page from the digital manga, uploaded as a teaser to drive purchases. Model:
`MangaPreviewPage`. Has a title (used as alt text). Featured in its own
section above Illustrations. Usually a few; no enforced cap. Shown in an
admin-defined order. Hidden from the page when unpublished.

**Published**
`is_published` flag; only published Events / Event Booth Photos / Illustrations / Manga Preview Pages appear on the
page. Defaults to true.
