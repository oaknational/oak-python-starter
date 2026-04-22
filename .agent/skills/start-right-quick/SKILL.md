---
name: start-right-quick
classification: active
description: >-
  Quick grounding at session start. Read directives, memory, check
  practice box, apply session priority order, then discuss with user.
---

# Start Right (Quick)

Session entry point. Ground yourself before starting work.

## Foundation Documents

Read and internalise before proceeding:

| Document | Purpose |
|----------|---------|
| `.agent/directives/AGENT.md` | Operational entry point, project context |
| `.agent/directives/principles.md` | Authoritative rules |
| `.agent/directives/testing-strategy.md` | TDD expectations and test types |
| `.agent/directives/metacognition.md` | Reflective thinking before planning |

## Memory

Read the learning loop files:

1. `.agent/memory/distilled.md` (if exists) — curated high-signal patterns
2. `.agent/memory/napkin.md` (if exists) — recent session context

## Guiding Questions

Before starting work, ask yourself:

1. **Right problem?** Am I solving what the user actually needs?
2. **Right layer?** Am I working at the correct level of abstraction?
3. **Could it be simpler?** The First Question — apply it now.
4. **What assumptions am I making?** Name them explicitly.

## Practice Box

Check `.agent/practice-core/incoming/` for incoming Practice Core files.
If files are present, alert the user — integration should happen via
the consolidation command.

If `.agent/practice-context/incoming/` exists, note its contents for
the user.

## Session Priority

Before choosing a lane, apply this order:

1. **Discovered bugs or regressions first.** If entry reading, local
   checks, or repo context reveals a bug, broken gate, contradictory
   canon, or behavioural regression, fix or triage that before any
   feature or planning continuation.
2. **Unfinished planned work second.** If no bugs are discovered,
   unresolved active-tranche completion work is the default priority.
   Use the relevant domain `current/README.md` to determine whether a
   live active tranche exists.
3. **New work last.** Start a fresh feature or research lane only after
   confirming there is no higher-priority unfinished tranche, or the
   user has explicitly superseded it.

## Process

1. Read all foundation documents
2. Read memory files
3. Check the Practice Box
4. Review the relevant domain `current/README.md` and identify whether
   the session is bug-fix, unfinished completion, or genuinely new work
5. If the current domain exposes unresolved completion work, open that
   plan before considering new feature or research work
6. If the task is **strategy research**, open
   `.agent/plans/strategy-research/current/README.md` and the most
   relevant cited evaluation artefact and reference doc before proceeding
7. If the task is **research infrastructure** (datasets, diagnostics,
   inference, realism, parity), open
   `.agent/plans/research-infrastructure/current/README.md` and the
   cited reference or evaluation material before proceeding
8. Review the current task list or plan (if any)
9. Discuss the first step with the user before proceeding

## Quality Gates

All quality gates are blocking. The gate sequence for this repo:

```
format-check -> typecheck -> lint -> import-boundaries -> repo-audit -> tests -> coverage
```

Entry point: `uv run check`
