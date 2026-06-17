# Thread: template-fitness-remediation

## Participating Agent Identities

| agent_name | platform | model | session_id_prefix | role | first_session | last_session |
| --- | --- | --- | --- | --- | --- | --- |
| Claude | claude | opus-4.8 | unknown | executor | 2026-06-17 | 2026-06-17 |

## Owning Plan

- [`../../../plans/runtime-infrastructure/current/template-fitness-remediation.md`](../../../plans/runtime-infrastructure/current/template-fitness-remediation.md)
- Source review: [`../../../reports/2026-06-17-python-repo-deep-review.md`](../../../reports/2026-06-17-python-repo-deep-review.md)

## Current Objective

Finish Phase 2 of the template-fitness remediation. **F4 (CI workflow) is now
landed and merged.** Remaining: **F3** (coverage honesty) and **F8** (chart
accessibility), then the F5/F6/F7 adoptability set. A parallel
quality-gate-surface-expansion workstream runs alongside (own thread).

## What Landed This Session (2026-06-17)

- **Deep review** across 11 orthogonal lenses with adversarial per-finding
  verification, plus a completeness critic → report (PR #7).
- **Remediation plan** authored and promoted to
  `runtime-infrastructure/current/` (PR #7).
- **Phase 1 (PR #8)**:
  - F1 — MIT `LICENCE`, a fresh `SECURITY.md`, PEP 639 metadata
    (`license = "MIT"` + `license-files`, `authors`, `keywords`, `classifiers`
    including `Typing :: Typed`, project URLs), a README licence section, and a
    new `repo_audit` `audit_distribution_metadata` check + required
    `LICENCE`/`SECURITY.md` paths.
  - F2 — deterministic CSV boundary (`dtype=str`, `keep_default_na=False`) so
    legitimate `NA`/`null` values are preserved instead of mis-rejected;
    out-of-range minutes rejected explicitly (int64-range guard). New tests.
- **Command-adapter rename (PR #9)**: `jc-` → `oak-` across all 44 adapters,
  the Codex `name:` frontmatter, `repo_audit` parity + its test, and doc
  references. Commands now invoke as `/oak-<name>`.
- Gates green throughout; **79 tests; coverage 88.1%**. The built wheel was
  verified to carry `License-Expression: MIT`, the packaged `LICENCE`, and the
  `Typing :: Typed` classifier.

## What Landed (2026-06-17, later session)

- **F4 — CI workflow (PR #11, merged).** `.github/workflows/ci.yml` runs
  `check-ci` on push + pull_request (Python 3.14, uv, least-privilege
  permissions, concurrency cancel, pinned actions, `cache-dependency-glob`).
  New `audit_ci_workflow` pins the contract. CI verified green on a real runner.
- The 6 Dependabot vulnerability PRs were verified green (full `check-ci` +
  CodeQL) and merged; Dependabot now has 0 open PRs.
- Reviewer agents and a Markdown gate also landed (see the
  quality-gate-surface-expansion thread).

## Next Session — Start Here (F3 → F8)

Each as its own feature branch + PR; UK spelling; gates green. Note: merges
require a PR through the repo ruleset (CodeQL `code_quality` check); see the
gate-expansion thread for the CodeQL/`update-branch` merge mechanics.

1. **F3 — coverage honesty.** Raise `fail_under` in `[tool.coverage.report]`
   from 70 toward the achieved ~88 (e.g. 85). Decide on the `devtools.py` omit
   (document the rationale inline if kept). Add `audit_coverage_contract` to
   `repo_audit` pinning the threshold floor and the exact omit-list so neither
   can silently weaken (the repo's own governance-claim-needs-a-scanner rule).
2. **F8 — chart accessibility (organisation WCAG 2.2 AA mandate).** In
   `default_chart_writer` (`demo/activity_report.py`): when `--chart` is given,
   also write a sibling text alternative from `render_summary` (SC 1.1.1);
   darken `PALETTE` colour `#d08d46` to clear 3:1 non-text contrast (it is
   2.77:1 on white) and give the target marker a contrasting halo (it is
   ~1.55:1 against blue bars) (SC 1.4.11). Add a test asserting the sidecar is
   written. **Required reading before starting F8**:
   [`reports/2026-06-17-python-repo-deep-review.md`](../../../reports/2026-06-17-python-repo-deep-review.md)
   — it holds the full `PALETTE`, both background values, and the marker base
   colour; the figures above are only a summary. Acceptance is ≥3:1 for every
   palette colour and the marker against both backgrounds.

Phase 3 (rename guide, trust-boundary note + size cap, guardrail
simplify-and-fail-close) and the deferred backlog are detailed in the plan.

## Key Decisions & Context (would be lost otherwise)

- **Excellence over convention is the owner's bar**: determine what excellent
  looks like and represent it fully; do not merely copy reference repos. Prefer
  modern best practice (e.g. PEP 639) and *verify* it (inspect the wheel). Do
  not cargo-cult — a fresh `SECURITY.md` was written, and the ecosystem's
  `ATTRIBUTION.md`/`LICENCE-DATA.md` were deliberately omitted (they exist only
  because that repo integrates external curriculum data).
- **Licence**: MIT, copyright holder "Oak National Academy".
- **UK/British spelling everywhere in repo-facing text is a hard rule** (hence
  `LICENCE`, "licence" the noun; the PEP 621 `license` key stays American by
  spec).
- **Dependabot is configured** (6 open dependency PRs as of 2026-06-17). This
  partially covers the supply-chain concern raised as F5 in the review, so read
  F5 with that in mind. Those PRs also want triage.
- **Commands are deprecated in favour of skills** (the ecosystem already
  migrated). Future agentic-engineering work, explicitly **not a priority**.
- The pre-commit/pre-push hooks run the full `check-ci`, which builds a real
  wheel in a temporary venv each time (~15–24 s) — commits are not instant.

## Blockers / Low-Confidence Areas

- None blocking Phase 2.
- 6 pre-existing Dependabot PRs are open and unmerged — triage is a separate,
  optional task.

## Next Safe Step

- Open a feature branch for **F4 (CI workflow)** and proceed through Phase 2 in
  order.
