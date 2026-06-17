# Thread: template-fitness-remediation

## Participating Agent Identities

| agent_name | platform | model | session_id_prefix | role | first_session | last_session |
| --- | --- | --- | --- | --- | --- | --- |
| Claude | claude | opus-4.8 | unknown | executor | 2026-06-17 | 2026-06-17 |

## Owning Plan

- [`../../../plans/runtime-infrastructure/current/template-fitness-remediation.md`](../../../plans/runtime-infrastructure/current/template-fitness-remediation.md)
- Source review: [`../../../reports/2026-06-17-python-repo-deep-review.md`](../../../reports/2026-06-17-python-repo-deep-review.md)

## Current Objective

Carry the template-fitness remediation through **Phase 2** (honest exemplars):
the CI workflow, coverage honesty, and chart accessibility. Phase 1 is landed.

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

## Next Session — Start Here (Phase 2)

Suggested order F4 → F3 → F8. Each as its own feature branch + PR; UK spelling;
gates green; rebase-merge for linear history.

1. **F4 — CI workflow.** Add `.github/workflows/ci.yml` running
   `uv run python -m oaknational.python_repo_template.devtools check-ci` on
   `push` + `pull_request`, Python 3.14, with `uv` setup. This is the first
   thing that exercises the installed-wheel smoke check for real (today every
   `devtools` test injects fakes, so it is only stubbed). Optionally add a
   `repo_audit` check that the workflow exists and invokes `check-ci`.
2. **F3 — coverage honesty.** Raise `fail_under` in `[tool.coverage.report]`
   from 70 toward the achieved ~88 (e.g. 85). Decide on the `devtools.py` omit
   (document the rationale inline if kept). Add `audit_coverage_contract` to
   `repo_audit` pinning the threshold floor and the exact omit-list so neither
   can silently weaken (the repo's own governance-claim-needs-a-scanner rule).
3. **F8 — chart accessibility (organisation WCAG 2.2 AA mandate).** In
   `default_chart_writer` (`demo/activity_report.py`): when `--chart` is given,
   also write a sibling text alternative from `render_summary` (SC 1.1.1);
   darken `PALETTE` colour `#d08d46` to clear 3:1 non-text contrast (it is
   2.77:1 on white) and give the target marker a contrasting halo (it is
   ~1.55:1 against blue bars) (SC 1.4.11). Add a test asserting the sidecar is
   written. Exact contrast figures are in the review report.

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
