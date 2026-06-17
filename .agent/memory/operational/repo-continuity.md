# Repo Continuity

**Last refreshed**: 2026-06-17 (later session) — CI is now live on `main`
(F4 merged), reviewer agents are registered with a Pythonicity lens, a Markdown
linting gate shipped, and the 6 open Dependabot vulnerability bumps were
verified green and merged. All 9 open PRs landed; `main` is green. Phase 2
(F3, F8) and a new quality-gate-surface-expansion workstream are queued.

## Active Threads

- **template-fitness-remediation** — F4 landed; **F3** (coverage honesty) and
  **F8** (chart accessibility) remain, then F5/F6/F7. See
  [`threads/template-fitness-remediation.next-session.md`](threads/template-fitness-remediation.next-session.md).
- **quality-gate-surface-expansion** — reviewer agents + Markdown gate done;
  **gitleaks, pip-audit, codespell, supply-chain config** queued. See
  [`threads/quality-gate-surface-expansion.next-session.md`](threads/quality-gate-surface-expansion.next-session.md).
- Closed references:
  [`threads/review-findings-closeout.next-session.md`](threads/review-findings-closeout.next-session.md),
  [`threads/pythonic-alignment.next-session.md`](threads/pythonic-alignment.next-session.md),
  and
  [`threads/practice-foundation-upgrade.next-session.md`](threads/practice-foundation-upgrade.next-session.md)

## Branch-Primary Lane State

- Phase 1 landed via PRs #7/#8/#9. This session merged **9 PRs**: F4 CI workflow
  (#11), reviewer agents (#12), Markdown gate (#13), and 6 Dependabot vulnerability
  bumps (#1–#6: requests, urllib3, idna, pillow, pygments, pytest).
- `main` is green (remote `CI [push]` success + local `check-ci`). 0 open PRs.

## Current Session Focus

- 2026-06-17 (later): shipped CI, reviewer agents, the Markdown gate; merged all
  open PRs (including the vuln bumps); updated all planning/continuation surfaces.
- Next: F3 → F8, plus the queued gate types (gitleaks, pip-audit, codespell,
  supply-chain config).

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
- Land work through feature branches and PRs. `main` is governed by a
  **repository ruleset**: a PR is required and a CodeQL `code_quality` check must
  pass; direct pushes are blocked. Merge mechanics (CodeQL trigger via
  `gh pr update-branch`, squash to flatten) are in the gate-expansion thread.

## Next Safe Step

- Resume Phase 2 with **F3** (coverage honesty), then **F8** (chart
  accessibility); and/or start the next gate type (**gitleaks**). Each its own
  feature branch off the current `main` + PR. Details in the two thread records
  and the two active plans.

## Open Side-Tasks

- Dependabot now has **0 open PRs** (the 6 vulnerability bumps were merged this
  session), so the F5 supply-chain concern is partially addressed; committing a
  `dependabot.yml` and pinning action SHAs remains queued in the gate-expansion
  plan.

## Deep Consolidation Status

- The 2026-06-17 later session captured its learning into the napkin, the two
  thread records, the two active plans, the gate-types review report, and the
  continuity/high-level surfaces.
- A full `consolidate-docs` graduation pass is optional and not yet due.
- The earlier 2026-04-23 source-Practice transfer remains the closed baseline.
