# Human Fossil

One-page site showcasing events and the booth photos taken at them.

## Glossary

**Event**
A dated gathering with a title and location. Shown in an *upcoming* section
(date today or later) or a *past* section. Single-day: no end date. Hidden from
the page when unpublished.

**Event Booth Photo**
Photo of the booth, optionally linked to an Event. Model: `EventPhoto`.
Featured in its own section, independent of Events. Survives deletion of its
Event (the link is cleared). Hidden from the page when unpublished.

**Published**
`is_published` flag; only published Events / Event Booth Photos appear on the
page. Defaults to true.
