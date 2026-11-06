# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`.human-fossil-vault/Domain/CONTEXT.md`**, or
- **`.human-fossil-vault/Domain/CONTEXT-MAP.md`** if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`.human-fossil-vault/ADRs/`** — read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo (most repos):

```
/
└── .human-fossil-vault/
    ├── Domain/
    │   └── CONTEXT.md
    └── ADRs/
        ├── 0001-event-sourced-orders.md
        └── 0002-postgres-for-write-model.md
```

Multi-context repo (presence of `Domain/CONTEXT-MAP.md`):

```
/
└── .human-fossil-vault/
    ├── Domain/
    │   ├── CONTEXT-MAP.md
    │   ├── ordering/CONTEXT.md
    │   └── billing/CONTEXT.md
    └── ADRs/                          ← all decisions, one dir
```

Even in the multi-context case, ADRs stay in the single `.human-fossil-vault/ADRs` dir — no per-context ADR directories. Use frontmatter or filename prefixes to scope an ADR to a context if needed.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
