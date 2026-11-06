## Agent skills

### Project vault

Obsidian vault at `.human-fossil-vault/`, home for knowledge notes, ADRs, reference material. See `docs/agents/vault.md`.

### Issue tracker

Vault is the tracker: specs and issues under `.human-fossil-vault/Projects/<slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Roles applied as frontmatter `tags:` on issue files. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: glossary at `.human-fossil-vault/Domain/CONTEXT.md`, ADRs at `.human-fossil-vault/ADRs`. See `docs/agents/domain.md`.

## Testing

Views: assert on `response.context` only. Never assert on rendered HTML/markup; templates change fast and such tests are brittle.
