# Repo Continuity

**Last refreshed**: 2026-06-17 — a deep multi-lens review landed, Phase 1 of the
template-fitness remediation shipped (licence + distribution metadata, and the
deterministic data boundary), and the command-adapter prefix was rebranded
`jc-` → `oak-`. Phase 2 is queued.

## Active Threads

- **template-fitness-remediation** — Phase 2 queued (CI workflow, coverage
  honesty, chart accessibility). See
  [`threads/template-fitness-remediation.next-session.md`](threads/template-fitness-remediation.next-session.md).
- Closed references:
  [`threads/review-findings-closeout.next-session.md`](threads/review-findings-closeout.next-session.md),
  [`threads/pythonic-alignment.next-session.md`](threads/pythonic-alignment.next-session.md),
  and
  [`threads/practice-foundation-upgrade.next-session.md`](threads/practice-foundation-upgrade.next-session.md)

## Branch-Primary Lane State

- Active lane: template-fitness remediation (runtime-infrastructure). Phase 1
  landed via PRs #7 (review report + plan), #8 (F1 licence/metadata + F2
  boundary), and #9 (`jc-` → `oak-` adapter rename). Phase 2 not yet started.

## Current Session Focus

- 2026-06-17: deep review, Phase 1, and the adapter rename landed on `main`.
  The next session continues with Phase 2 (start with the CI workflow).

## Repo-Wide Invariants / Non-Goals

- Preserve the repo's Python-first runtime and `uv`-managed workflow.
- Keep the Practice portable, but adapt it truthfully to Python where the
  source repo assumes Node-specific mechanics.
- Do not import source-repo historical residue that breaks this repo's audit or
  identity.
- Keep `oaknational.*`, strict gates, and Practice governance as fixed
  constraints.
- Judge work by excellence (what the template should model), not mere
  convention; UK/British spelling everywhere in repo-facing text.
- Land work through feature branches and PRs.

## Next Safe Step

- Begin Phase 2: open a feature branch for the CI workflow (F4), then coverage
  honesty (F3) and chart accessibility (F8). Details in the thread record and
  the active plan.

## Open Side-Tasks

- 6 Dependabot dependency PRs are open and unmerged (pre-existing). Triage when
  convenient; their existence means basic supply-chain monitoring is in place
  (a refinement to the review's F5 framing).

## Deep Consolidation Status

- The 2026-06-17 session captured its learning into the napkin, a new
  `template-fitness-remediation` thread record, an experience note, the active
  plan, and the executive/continuity surfaces.
- A full `consolidate-docs` graduation pass is optional and not yet due.
- The earlier 2026-04-23 source-Practice transfer remains the closed baseline.
