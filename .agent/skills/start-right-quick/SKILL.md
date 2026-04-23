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
| `.agent/directives/orientation.md` | Layering and authority order |
| `.agent/directives/metacognition.md` | Reflective thinking before planning |

## Memory

Read the three memory planes:

1. `.agent/memory/README.md` — memory contract and authority order
2. `.agent/memory/active/distilled.md` (if exists) — curated high-signal patterns
3. `.agent/memory/active/napkin.md` (if exists) — recent session context
4. `.agent/memory/operational/repo-continuity.md` (if exists) — continuity state
5. `.agent/plans/high-level-plan.md` — strategic cross-collection context

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
4. Review the relevant collection `current/README.md` and identify whether
   the session is bug-fix, unfinished completion, or genuinely new work
5. If the current collection exposes unresolved completion work, open that
   plan before considering new feature or research work
6. If the task needs a deeper document tier, open the relevant `research/`,
   `analysis/`, `reports/`, `reference/`, or `docs/explorations/` surface
7. Review the current task list or plan (if any)
8. If an active thread exists, open its next-session record before proceeding
9. Discuss the first step with the user before proceeding

## Quality Gates

All quality gates are blocking. The gate sequence for this repo:

```
format -> typecheck -> lint -> import-linter -> dependency-hygiene -> repo-audit -> build -> test -> coverage
```

Non-mutating gate entry point:
`uv run python -m oaknational.python_repo_template.devtools check-ci`
Local fix-and-verify aggregate:
`uv run python -m oaknational.python_repo_template.devtools check`
