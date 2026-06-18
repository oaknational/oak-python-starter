# Repo Continuity

**Last refreshed**: 2026-06-18 — mid-program checkpoint (session split for
context). Since the last refresh: gitleaks gate (#16), coverage→GitHub Code
Quality (#18), **release automation** (release-PR pattern, live-verified —
`v0.1.0` + `v0.2.0` released), **pip-audit** gate (#24), **codespell** gate
(#26) all merged; `main` is green at `v0.2.0`. An owner-approved
**"highest proportionate bar" program** (4 lanes) is in progress — Tier 1a
nearly done (supply-chain pinning in flight), Tiers 1b/3/2 queued. Full program
state + the critical release-PR `--auto` mechanic live in the
[gate-expansion thread record](threads/quality-gate-surface-expansion.next-session.md).

## Active Threads

- **quality-gate-surface-expansion → "highest proportionate bar" program**
  (the live spine) — gitleaks/pip-audit/codespell gates, coverage publishing, and
  release automation all **done**; supply-chain pinning **in flight** (branch
  `feat/supply-chain-pinning`, no PR yet); Tier 1b (F3/F8/F5-7), Tier 3
  (Pythonic), Tier 2 (governance) queued. Tier 4 deliberately deferred. The
  thread record is the authoritative program handoff. See
  [`threads/quality-gate-surface-expansion.next-session.md`](threads/quality-gate-surface-expansion.next-session.md).
- **template-fitness-remediation** — F1/F2/F4 landed; **F3/F8/F5-7** remain and
  are now folded into the program's Tier 1b. See
  [`threads/template-fitness-remediation.next-session.md`](threads/template-fitness-remediation.next-session.md).
- Closed references:
  [`threads/review-findings-closeout.next-session.md`](threads/review-findings-closeout.next-session.md),
  [`threads/pythonic-alignment.next-session.md`](threads/pythonic-alignment.next-session.md),
  and
  [`threads/practice-foundation-upgrade.next-session.md`](threads/practice-foundation-upgrade.next-session.md)

## Branch-Primary Lane State

- Merged this program: #16 gitleaks, #18 coverage→Code Quality, #19/#20/#22
  release automation, #24 pip-audit, #26 codespell. `main` is green at `v0.2.0`.
- **Open: release PR #25 `chore(release): v0.3.0`** (standing, intentionally
  accumulating — merge with `--auto` at sprint end). **Pushed, no PR: branch
  `feat/supply-chain-pinning`** (action SHA-pins + dependabot.yml).
- Releases cut + verified: **`v0.1.0`, `v0.2.0`** (wheel + sdist attached).
- Coverage `fail_under` still 70 (achieved ~88); raising it is Tier 1b / F3.

## Current Session Focus

- 2026-06-18: drove the gap analysis + the owner-approved 4-lane program; landed
  pip-audit + codespell; checkpointing mid-program (supply-chain in flight) to
  split the remaining work across sessions and avoid low-context burden.
- Next: finish supply-chain PR → Tier 1b (F3/F8/F5-7) → Tier 3 → Tier 2; then
  merge release PR #25. Authoritative detail in the gate-expansion thread record.

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
- Repo naming (a known drift F7 will reconcile): working dir
  `python-repo-template`, distribution `oaknational-python-repo-template`, but
  the GitHub remote and `[project.urls]` slug is `oaknational/oak-python-starter`
  — use that slug for `gh`/remote operations.
- Land work through feature branches and PRs. `main` is governed by a
  **repository ruleset**: a PR is required and a CodeQL `code_quality` check must
  pass; direct pushes are blocked. Merge mechanics (CodeQL trigger via
  `gh pr update-branch`, squash to flatten) are in the gate-expansion thread.

## Next Safe Step

- Open the **supply-chain PR** from `feat/supply-chain-pinning` (optionally add
  the `audit_supply_chain` self-check first), verify green, merge. Then Tier 1b
  (F3 → F8 → F5/6/7), Tier 3 (branch coverage, Hypothesis, version-policy ADR),
  Tier 2 (governance checklist). Finally **merge release PR #25 with `--auto`**
  to cut the accumulated release. Authoritative detail + the `--auto`/UNSTABLE
  mechanic are in the gate-expansion thread record.

## Open Side-Tasks

- **Owner actions (settings, not code):** add "Quality gates" + "Secret scanning"
  to the ruleset's required checks; provide a release-PR PAT/App token; enable
  GitHub Code Quality preview; add `v*` tag protection. (See thread record.)
- **Deferred to fresh context:** a deep `consolidate-docs` graduation (home
  durable doctrine, archive the done release-automation plan, rotate the napkin).
- Re-check the Dependabot security-alert count before assuming zero open vulns
  (pip-audit now scans the locked set in `check-ci`, so new advisories surface).

## Deep Consolidation Status

- The 2026-06-17 later session captured its learning into the napkin, the two
  thread records, the two active plans, the gate-types review report, and the
  continuity/high-level surfaces.
- A full `consolidate-docs` graduation pass is optional and not yet due.
- The earlier 2026-04-23 source-Practice transfer remains the closed baseline.
