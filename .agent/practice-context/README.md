# Practice Context

This directory is optional and sits outside the portable Practice Core.

The Core remains the required package in `.agent/practice-core/`. This
directory is for lightweight, ephemeral exchange context only.

## Structure

- `outgoing/` - sender-maintained ephemeral support notes
- `incoming/` - received support material and temporary integration notes

`incoming/` is transient. Clear received files after integration.
`outgoing/` may persist, but it should stay lightweight.

Durable governance belongs in `.agent/practice-core/decision-records/`.
Portable general patterns belong in `.agent/practice-core/patterns/`.
Repo-local proven instances belong in `.agent/memory/active/patterns/`.

When `outgoing/` contains more than one note, keep it indexed and separate the
documents by purpose.
