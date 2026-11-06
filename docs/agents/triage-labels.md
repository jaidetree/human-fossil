# Triage Labels

The skills speak in terms of five canonical triage roles. In this repo's tracker (the Obsidian vault), these roles are applied as frontmatter `tags:` on issue files — not as tracker labels.

| Label in mattpocock/skills | Tag in this vault | Meaning                                  |
| --------------------------- | ------------------ | ----------------------------------------- |
| `needs-triage`               | `needs-triage`      | Maintainer needs to evaluate this issue   |
| `needs-info`                 | `needs-info`        | Waiting on reporter for more information  |
| `ready-for-agent`            | `ready-for-agent`   | Fully specified, ready for an AFK agent   |
| `ready-for-human`            | `ready-for-human`   | Requires human implementation             |
| `wontfix`                    | `wontfix`           | Will not be actioned                      |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), set the corresponding tag in the issue file's `tags:` frontmatter. See `docs/agents/issue-tracker.md` for how tags relate to an issue's folder (dev state).
