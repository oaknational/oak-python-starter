# Repo Continuity

**Last refreshed**: 2026-06-18 (later) — **supply-chain PR #28 opened**. The
`feat/supply-chain-pinning` branch now carries (all committed, HEAD `f5225cb`):
action SHA-pins + `dependabot.yml` + the `audit_supply_chain` self-check + the
incidental packaging-schema fix (below). **PR #28 is open and awaiting CI + the
SonarCloud gate green, then merge.** Earlier this program:
gitleaks gate (#16), coverage→GitHub Code Quality (#18), **release automation**
(live-verified — `v0.1.0` + `v0.2.0` released), **pip-audit** gate (#24),
**codespell** gate (#26) all merged; `main` is green at `v0.2.0`. An
owner-approved **"highest proportionate bar" program** (4 lanes) is in progress —
Tier 1a effectively done (supply-chain in PR #28), Tiers 1b/3/2 queued.
Full program state + the critical release-PR `--auto` mechanic live in the
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
  accumulating — merge with `--auto` at sprint end).
- **Open: supply-chain PR #28** (branch `feat/supply-chain-pinning`, HEAD
  `f5225cb`): action SHA-pins + `dependabot.yml` + `audit_supply_chain`
  self-check, plus the packaging-schema fix below. Awaiting CI + SonarCloud green.
- **Folded into PR #28** (committed by this session): a packaging-schema fix —
  `pyproject.toml` `[tool.hatch.build.targets.wheel].sources` `["src"]` →
  `{ "src" = "" }` (the array tripped the *Even Better TOML* SchemaStore Hatch
  schema, which types `sources` as an object; both forms build byte-identical
  wheels), plus **removal** of the `audit_packaging_contract` audit + its test
  (it asserted config *shape*, a testing-strategy violation — the packaging
  behaviour is already proven by the build-gate wheel-smoke). Do **not** re-add
  it or a wheel-namelist test in its place.
- **NEW — SonarCloud is a live PR quality gate** (`SonarCloud Code Analysis`
  check), org-level automatic analysis (no `sonar-project.properties` in-repo).
  It is **not** a *required* status check on the `main` ruleset, but its gate is
  blocking by repo doctrine. It fails on new-code conditions, e.g.
  `new_code_smells_severity` (PR #28's first push tripped it: cognitive
  complexity > 15 + a duplicated literal). Query it with the SonarQube MCP:
  `get_project_quality_gate_status` / `search_sonar_issues_in_projects`,
  projectKey `oaknational_oak-python-starter`, `pullRequest <n>`.
- Releases cut + verified: **`v0.1.0`, `v0.2.0`** (wheel + sdist attached).
- Coverage `fail_under` still 70 (achieved ~88); raising it is Tier 1b / F3.

## Current Session Focus

- 2026-06-18: drove the gap analysis + the owner-approved 4-lane program; landed
  pip-audit + codespell; checkpointing mid-program (supply-chain in flight) to
  split the remaining work across sessions and avoid low-context burden.
- 2026-06-18 (later): committed the supply-chain work + the packaging-schema fix
  (handed over from a now-closed parallel session) and **opened PR #28**. Ran
  config/security/code reviewers pre-PR and adopted the substantive findings
  (docker `sha256:` digest acceptance, job-level reusable-workflow `uses:`
  coverage, `.yaml` globbing, no double-failure on malformed dependabot, DRY
  helper extraction). Verified all four pinned action SHAs match their upstream
  `vN` tags. SonarCloud flagged two new-code smells on the first push → fixed by
  decomposing `audit_supply_chain`; awaiting the Sonar re-run.
- Next: get PR #28 green (CI + SonarCloud) → merge → Tier 1b (F3/F8/F5-7) →
  Tier 3 → Tier 2; then merge release PR #25. Authoritative detail in the
  gate-expansion thread record.

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

- **Get supply-chain PR #28 green** (CI + the SonarCloud gate) and **merge**
  (it is a normal PR, so CodeQL triggers and `gh pr merge 28 --squash
  --delete-branch` once green — not the bot-PR `--auto` path). Then Tier 1b
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
- 2026-06-18 (later): ran a light `consolidate-docs` pass alongside the
  packaging-fix handoff. Findings: incoming Practice boxes empty (only a
  placeholder dir); napkin 160 lines (no rotation due); this session's lesson
  already lives in `testing-strategy.md` (nothing to graduate); plan/thread/
  continuity reconciled. **The deep graduation remains DEFERRED to a dedicated
  fresh-context session** — specifically archiving the **release-automation
  plan** (marked DELIVERED & LIVE-VERIFIED; needs its release doctrine homed +
  move to `archive/` + `completed-plans.md` row + index/link fixes). Not done
  now by design (low-context risk on a 5-surface plan operation).
- The earlier 2026-04-23 source-Practice transfer remains the closed baseline.
