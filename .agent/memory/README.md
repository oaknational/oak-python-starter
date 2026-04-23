# Memory

This repo now uses the full three-plane memory estate:

- **active** — the learning loop
- **operational** — continuity and session-resume state
- **executive** — stable organisational contracts

These surfaces are read and written. They are distinct from directives, which
are read-and-internalise doctrine, and from reference docs, which are
read-to-learn supporting material.

## The Three Planes

### [`active/`](active/) — learning-loop memory

Purpose: capture, distil, and graduate lessons from real work.

Contents:

- [`active/napkin.md`](active/napkin.md) — session capture
- [`active/distilled.md`](active/distilled.md) — curated high-signal lessons
- [`active/patterns/`](active/patterns/) — repo-local reusable patterns
- [`active/archive/`](active/archive/) — rotated napkins and related capture

Read at session start and update continuously while working.

### [`operational/`](operational/) — continuity memory

Purpose: answer "where are we right now, what is live, and what should the
next session do?"

Contents:

- [`operational/repo-continuity.md`](operational/repo-continuity.md) —
  canonical repo-level continuity contract
- [`operational/threads/`](operational/threads/) — per-thread next-session
  records
- [`operational/tracks/`](operational/tracks/) — tactical coordination cards
- [`operational/workstreams/`](operational/workstreams/) — retired surface,
  preserved as doctrine and provenance only
- [`operational/diagnostics/`](operational/diagnostics/) — operational logs and
  notes when a continuity mechanism needs lightweight evidence

Read when resuming work or changing threads. Refresh through
`session-handoff`.

### [`executive/`](executive/) — stable contract memory

Purpose: hold organisational catalogues that govern how the repo is structured.

Contents:

- [`executive/artefact-inventory.md`](executive/artefact-inventory.md)
- [`executive/invoke-code-reviewers.md`](executive/invoke-code-reviewers.md)
- [`executive/cross-platform-agent-surface-matrix.md`](executive/cross-platform-agent-surface-matrix.md)

Look these up when adding or reviewing governed surfaces. They do not need
session-start rereads unless the current task depends on them.

## Authority Order

When operational surfaces disagree on the same field:

1. Plans own scope, sequencing, and acceptance criteria.
2. `operational/repo-continuity.md` owns repo-level continuity.
3. `operational/threads/<slug>.next-session.md` owns thread-level continuity.
4. `operational/tracks/*.md` are tactical only and never define scope.
