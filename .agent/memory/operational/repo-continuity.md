# Repo Continuity

**Last refreshed**: 2026-06-18 (final+) — the "highest proportionate bar" program
is COMPLETE. **The release model is now CONTINUOUS release on merge (PR #44),
PR-merge-ONLY** — the release-PR/`--auto` pattern AND the manual `workflow_dispatch`
are both gone (owner: releases originate only from a merge to `main`; the rare
major is cut by a human outside this repo's automation). After CI passes on `main`,
the Oak Semantic Release Bot (app 2995796, a ruleset bypass actor) bumps + tags +
pushes to `main` and publishes the Release. **Live-verified** (a clean merge cut a
release end-to-end; the bot's push-to-protected-`main` works). Don't write specific
future version numbers in durable docs — they go stale; describe the mechanism.
Required status checks (Quality gates, Secret scanning, CodeQL, SonarCloud) and a
`v*` tag ruleset are now enforced in GitHub settings.

(Earlier this session, pre-#44:) `main` is green. Landed: **F6** agent-hook hardening (#37, owner
chose recurse-and-check), **Tier 3** branch coverage + floor 86 (#38), Hypothesis
property tests (#39), single-version ADR-0002 (#40), **Tier 2** governance
checklist `docs/repository-governance.md` (#41), **Dependabot** #29 (actions) +
#30 (14 python deps) verified-and-merged, then **release PR #25 → `v0.3.0`** via
`--auto`. Earlier in the program: gitleaks (#16), coverage→Code Quality (#18),
release automation (`v0.1.0`/`v0.2.0`), pip-audit (#24), codespell (#26),
supply-chain (#28), F3/F8/F5/F7 (#31/#33/#34). **Tier 4 stays deliberately
deferred.** Remaining work is **owner-only settings** (`docs/repository-governance.md`)
plus documented F6 residuals (glued shell operators, bare subshells, heredoc-prose
over-block). Full state in the
[gate-expansion thread record](threads/quality-gate-surface-expansion.next-session.md).

## Active Threads

- **quality-gate-surface-expansion → "highest proportionate bar" program**
  — **COMPLETE.** All gates, coverage publishing, supply-chain pinning, Tier 1b
  (F3/F8/F5/F6/F7), Tier 3, and Tier 2 landed; Tier 4 deliberately deferred. A
  follow-on **release-model overhaul** (continuous-on-merge, PR-merge-only) also
  landed and is verified. The thread record (with its supersession banner) is the
  authoritative handoff. See
  [`threads/quality-gate-surface-expansion.next-session.md`](threads/quality-gate-surface-expansion.next-session.md).
- **template-fitness-remediation** — **COMPLETE** (F1–F8 all landed; F6 via #37).
  See
  [`threads/template-fitness-remediation.next-session.md`](threads/template-fitness-remediation.next-session.md).
- Closed references:
  [`threads/review-findings-closeout.next-session.md`](threads/review-findings-closeout.next-session.md),
  [`threads/pythonic-alignment.next-session.md`](threads/pythonic-alignment.next-session.md),
  and
  [`threads/practice-foundation-upgrade.next-session.md`](threads/practice-foundation-upgrade.next-session.md)

## Branch-Primary Lane State

- Merged this program: #16 gitleaks, #18 coverage→Code Quality, #19/#20/#22
  release automation, #24 pip-audit, #26 codespell, **#28 supply-chain pinning +
  `audit_supply_chain` + packaging-schema fix**, **#31 honest coverage floor
  (85) + `audit_coverage_contract`**, **#33 WCAG 2.2 AA accessible chart (F8)**,
  **#34 remote size-cap (F5) + rename guide (F7)**. `main` is green.
- **Tier 1b F6 DONE** (#37, recurse-and-check agent-hook hardening).
- **Release PR #25 / the release-PR + `--auto` pattern: SUPERSEDED.** #25 merged
  (cut `v0.3.0`); releases are now continuous-on-merge, PR-merge-only (see the
  header and the gate-expansion thread record's supersession banner).
- **Folded into PR #28** (merged): a packaging-schema fix —
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
- Coverage `fail_under` is now **85** (achieved ~88), pinned by
  `audit_coverage_contract` (#31). F3 done.

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
- 2026-06-18 (later still): merged PR #28; then landed **Tier 1b F3** as PR #31
  (honest coverage floor 85 + `audit_coverage_contract`), config-reviewed (fixed
  a false-positive on an absent `omit` key) and merged. Checkpointing here so the
  WCAG work (F8) starts with fresh context.
- 2026-06-18 (later still, cont.): landed **F8** (PR #33, WCAG chart — code-review
  adopted) and **F5+F7** (PR #34, remote size-cap + rename guide — security-review
  adopted the connection-closing `with` and `stream=True` assertions). **Deferred
  F6** (the `agent_hooks.py` guardrail) on safety/ambiguity grounds — see the
  thread record. Tier 1b is complete bar F6.
- 2026-06-18 (final): all of the above landed — F6 (#37), Tier 3 (#38/#39/#40),
  Tier 2 (#41), Dependabot (#29/#30), release `v0.3.0` (#25). Then an
  owner-directed **release-model overhaul**: continuous release on merge,
  PR-merge-only, via the bot (#44/#46); PyPI guide + gates overview (#47);
  `v0.4.0`/`v0.4.1` cut and verified. Release automation is done — see the header
  and the gate-expansion thread record's supersession banner for the current
  model. Cross-repo `client-id` fix opened on oak-open-curriculum (their PR #214).

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

- **Release automation is done and verified** (continuous, PR-merge-only). No
  queued release work. Remaining: (1) **owner-only GitHub setting** — enable the
  GitHub Code Quality org preview (the required checks + `v*` tag ruleset +
  release-bot secrets/bypass are all in place); (2) **PyPI publishing guide** for
  adopters (in progress this session — docs-only); (3) **F6 residuals** (glued
  shell operators like `ok|git`, bare subshells, heredoc-prose over-block) —
  deferred, the glued-operator one needs a quote-aware raw tokeniser; (4) **Tier 4**
  stays deferred. Normal PRs merge with `gh pr merge <n> --squash --delete-branch`
  once green — keep the literal CI-skip token out of the commit/PR message or the
  squash-merge skips CI and no release fires.

## Open Side-Tasks

- **Owner actions (settings, not code):** mostly DONE (verified via API) —
  required checks (Quality gates, Secret scanning, CodeQL, SonarCloud) enforced,
  `v*` tag ruleset added, release-bot secrets (`RELEASE_APP_CLIENT_ID` +
  private key) + bypass actor in place. **Only remaining:** enable the GitHub
  Code Quality org preview. (The release-PR token action is obsolete — the bot
  pushes directly now.) See `docs/repository-governance.md`.
- Re-check the Dependabot security-alert count before assuming zero open vulns
  (pip-audit now scans the locked set in `check-ci`, so new advisories surface).

## Deep Consolidation Status

- The 2026-06-17 later session captured its learning into the napkin, the two
  thread records, the two active plans, the gate-types review report, and the
  continuity/high-level surfaces.
- 2026-06-18 (deep pass): ran a full `consolidate-docs` at end of the Tier 1b
  session. **Archived the release-automation plan** to
  `runtime-infrastructure/archive/` (doctrine confirmed homed in README "##
  Releases", `docs/dev-tooling.md`, the `release.yml` comment,
  `tools/release_increment.py`, and `audit_release_workflow`); added its
  `completed-plans.md` row and archive index entry; fixed the thread-record link;
  refreshed `current/README.md` to current reality. Distilled the session's
  settled lessons into `distilled.md` and added a session experience note.
  Incoming Practice boxes empty (no-op). Napkin 222 lines — under the rotation
  threshold, left in place. Both remaining `current/` plans
  (quality-gate-surface-expansion as the live program spine; template-fitness
  with only F6 left) are deliberately kept open.
- 2026-06-18 (final, post-overhaul): ran `consolidate-docs` after the
  release-model overhaul. Durable doctrine was homed inline during the work
  (README "## Releases" + "## Quality gates & CI/CD", `docs/dev-tooling.md`,
  `docs/repository-governance.md`, `docs/publishing-to-pypi.md`, `release.yml`,
  `audit_release_workflow`). This pass: added the supersession banner + corrected
  the stale `--auto` mechanics in the gate-expansion thread record; annotated the
  archived release-automation plan as superseded; refreshed continuity (F6 done,
  the release-PR pattern superseded, owner-actions mostly done); added a
  release-model experience note. Incoming Practice boxes empty (no-op). Napkin 294 lines —
  under the rotation threshold, left in place; `distilled.md` unchanged
  (durable lessons already homed in docs).
- The earlier 2026-04-23 source-Practice transfer remains the closed baseline.
