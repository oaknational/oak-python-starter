---
name: "Template Fitness Remediation"
overview: "Fix the fundamental blockers to this repo serving as a demonstration, teaching aid, and template basis for future repos."
todos:
  - id: licence-metadata
    content: "F1 — add LICENCE and [project] distribution metadata."
    status: pending
  - id: boundary-correctness
    content: "F2 — make the CSV boundary robust to pandas NA/dtype sniffing, with negative tests."
    status: pending
  - id: honest-gates
    content: "F3 — raise coverage threshold toward achieved and audit the omit-list."
    status: pending
  - id: ci-workflow
    content: "F4 — add a CI workflow that runs check-ci on push and PR."
    status: pending
  - id: accessible-output
    content: "F8 — emit a text alternative for the chart and lift failing contrasts."
    status: pending
  - id: adoptability
    content: "F5/F6/F7 — trust-boundary note + size cap, guardrail simplify-and-fail-close, rename guide."
    status: pending
---

# Template Fitness Remediation

**Last Updated**: 2026-06-17
**Status**: 🟡 PLANNING
**Scope**: the fundamental blockers to this repo serving as a demonstration, teaching aid, and template basis for future repos.
**Source**: [Deep-Dive Review 2026-06-17](../../../reports/2026-06-17-python-repo-deep-review.md).

## End Goal

A future Oak team can clone this repo, legally reuse it, and trust that every pattern it demonstrates is correct and enforced. Specifically: the package is licensed and publishable; the flagship "validate at the boundary" example accepts legitimate data; the quality gates protect what they claim; CI exists; and produced artefacts meet the organisation's WCAG 2.2 AA mandate.

## Mechanism

Each fix is chosen to be the *smallest truthful change that doubles as a good teaching example*. We fix the demonstrated behaviour (not just the symptom), attach a deterministic validation command to each change, and prove boundary fixes with negative tests — because a teaching aid is judged by what it models, not only by whether it runs.

## Context

The deep-dive review found no blockers to *running* the repo (all gates green, 75 tests, 88% coverage) but several **fundamental blockers to its stated purpose**:

- It is legally unusable as a base for new repos (no licence).
- Its central lesson — strict boundary validation — mis-rejects valid input.
- Its honesty exemplars (coverage gate, CI) are weaker than they appear.
- Its only graphical artefact misses the organisation's accessibility mandate.

## Root Cause

The repo optimised for **internal contract enforcement** (a 1666-line auditor, a recursive hook parser) while leaving **outward-facing reusability fundamentals** (licence, distributable metadata, CI, boundary robustness against real-world data) unaddressed. The machinery is aimed at the wrong risks for a template.

## Existing Capabilities

- `render_summary` already produces a complete, accessible text representation of the chart data — reuse it as the chart's text alternative (F8).
- `tools/repo_audit.py` already has the `audit_*` pattern and a contract-checked-docs discipline — extend it to pin the coverage config (F3).
- The injected-seam test convention (`csv_loader`, `remote_reader`, …) makes the boundary fix easy to test without monkeypatching (F2).
- `gate_contract.toml` + `gate_registry` give a single command surface a CI workflow can call verbatim (F4).

## Strategy

Three ordered phases. Phase 1 removes the two true blockers (you cannot base a repo on an unlicensed template, and you must not teach a boundary that rejects valid data). Phase 2 restores the honesty exemplars (gates, CI, accessible output). Phase 3 is adoptability hardening that is valuable but not blocking. Everything else is explicitly deferred (see Non-Goals and the Deferred Backlog) so this plan stays proportionate.

## First-Principles Check

- **Is "strict boundary validation" the right teaching, given F2?** Yes — the lesson is right; the implementation trusts pandas' defaults instead of declaring them. The fix is to make the boundary deterministic (`keep_default_na=False`, explicit dtypes), which *strengthens* the lesson rather than weakening it.
- **Do we need an SSRF framework (F5)?** No. For a local demo CLI the user supplies the URL; a full allow-list would be gold-plating. A size cap plus an honest trust-boundary note is the proportionate, teachable answer.
- **Should we add more shell parsing to close the guardrail gap (F6)?** No — the parser is already over-built. Fail-closed and simplify; the guardrail is advisory defence-in-depth, not a security boundary.
- **Is a rename automation tool warranted (F7)?** Not yet — a documented rename procedure clears the blocker; a script is optional. Build-vs-buy: no existing Oak rename tool was found, and a guide is cheaper than a tool to maintain.

## Phase 1 — Fundamental blockers

### F1 — Licence and distribution metadata
- **Decision required (owner)**: which licence (recommend matching Oak's standard open-source code licence, e.g. MIT; the ecosystem repo uses a British-spelled `LICENCE`).
- **Means**: add a root `LICENCE` file; add `license`, `license-files`, `authors`, `classifiers` (incl. `Programming Language :: Python :: 3.14`), and `urls` to `[project]`.
- **Acceptance**: the built wheel METADATA carries the licence and classifiers; `repo_audit` gains an `audit_distribution_metadata` check asserting these keys exist.
- **Validate**: `uv run python -m oaknational.python_repo_template.devtools build` then inspect wheel METADATA; `... devtools repo-audit`.

### F2 — Deterministic CSV boundary
- **Means**: in `default_csv_loader` (and the remote CSV path) pass `keep_default_na=False` and an explicit `dtype`/converter set so `NA`/`null`/`None` category and note cells, and thousands-separated numbers, are not silently mangled before validation. Keep the validators as the single source of rejection.
- **Acceptance**: new negative/positive tests prove `category="NA"` is **accepted**, `notes="NA"` is preserved literally, and the existing reject paths (empty, fractional, non-positive, wrong columns) still fire with their exact messages.
- **Validate**: `... devtools test` and `... devtools coverage`.

## Phase 2 — Core quality for a teaching template

### F3 — Honest coverage gate
- **Means**: raise `fail_under` toward the achieved level (≈85); either remove the `devtools.py` omit or document its rationale inline; add `audit_coverage_contract` to `repo_audit` pinning the threshold floor and the exact omit-list.
- **Acceptance**: lowering `fail_under` or silently extending the omit-list fails `repo-audit`.
- **Validate**: `... devtools coverage`; `... devtools repo-audit`.

### F4 — CI workflow
- **Means**: add `.github/workflows/ci.yml` running `uv run python -m oaknational.python_repo_template.devtools check-ci` on push and pull_request, on Python 3.14. This also exercises the wheel-smoke for real (today only stubbed).
- **Acceptance**: the workflow runs green; `repo_audit` optionally asserts the workflow exists and invokes `check-ci`.
- **Validate**: CI run on a branch; `... devtools check-ci` locally.

### F8 — Accessible chart output (organisation WCAG 2.2 AA mandate)
- **Means**: when `--chart` is given, also write a sibling text alternative from `render_summary` (SC 1.1.1); darken `#d08d46` to clear 3:1 non-text contrast and give the target marker a contrasting halo (SC 1.4.11).
- **Acceptance**: a test asserts the sidecar text file is written and matches the report; recomputed contrast for every palette colour and the target marker is ≥3:1 against both backgrounds.
- **Validate**: `... devtools test`; manual chart render.

## Phase 3 — Adoptability hardening (recommended, non-blocking)

- **F7 — Rename guide**: add an "Adapting this template" section (rename steps for distribution/import/script names and the auditor constants); optionally a small `scripts/rename.py`. Consider driving the auditor's identity expectations from one declared source.
- **F5 — Trust boundary**: add a response-size cap to `default_remote_reader` and a short note (README or ADR) stating the remote-fetch trust model.
- **F6 — Guardrail**: treat `|` as a segment separator and fail-closed on `$(`/backticks in a git-bearing segment in `agent_hooks.py`; add allow-path tests (`git commit`, `git push`, `git status` must be allowed).

## Non-Goals

- **Migrating `.agent/commands/` to skills.** Confirmed deprecated and eventually-needed, but explicitly **not a priority** (owner steer 2026-06-17). Tracked in the Deferred Backlog.
- Full SSRF allow-listing or supply-chain vulnerability scanning (disproportionate for a demo).
- A rename *automation tool* (a documented procedure clears the blocker).
- Rewriting `repo_audit.py` or de-duplicating every SSOT seam (Deferred Backlog).

## Deferred Backlog (real, not pressing)

- **Commands → skills migration** (12 commands + `jc-*` adapters + `_audit_command_parity`); the ecosystem repo has already migrated. Future agentic-engineering work.
- SSOT erosion: dead `gate_registry.repo_local_command_targets()`; duplicated pyright config; triplicated TOML helpers; `gate_steps` bare `KeyError` → helpful error.
- `repo_audit.py` down-scoping; an ADR recording the deliberate bleeding-edge stack.
- Minor correctness: int64 saturation, Parquet date message, wheel mtime tiebreak, double validation, double test run, `dev` cwd-dependence, non-atomic writes.
- Background: ADR-0001 dead link, GitHub session-start hook + matrix legend, practice-index link scanner.

## Acceptance Criteria (whole plan)

1. `LICENCE` exists and the wheel carries licence + classifier metadata, audited.
2. The CSV boundary accepts legitimate `NA`/`null`/thousands data and still rejects genuinely invalid data, proven by tests.
3. `fail_under` reflects achieved coverage and the omit-list is audited.
4. A CI workflow runs `check-ci` on push/PR.
5. The chart ships a text alternative and all chart contrasts meet WCAG 2.2 AA.
6. `... devtools check-ci` stays green throughout.

## Foundation Alignment

- [principles.md](../../../directives/principles.md) — First Question, validate at boundary, fail fast.
- [data-boundary-doctrine.md](../../../directives/data-boundary-doctrine.md) — F2.
- [testing-strategy.md](../../../directives/testing-strategy.md) — negative tests for each reject path.
- Rules: `strict-validation-at-boundary`, `fail-fast-with-helpful-errors`, `all-quality-gate-issues-are-always-blocking`, `governance-claim-needs-a-scanner` (F3 audit).
- Organisation mandate: artefacts WCAG 2.2 AA; no PII (F8).

## Reviewer Phase Alignment

- **Plan-time**: architecture-reviewer on this plan's scope and the F3 audit shape.
- **Mid-cycle**: security-reviewer on F5; test-reviewer on F2/F8 tests; config-reviewer on F3/F4.
- **Close**: code-reviewer for whole-change coherence and documentation fit.

## Risk Assessment

| Risk | Mitigation |
| --- | --- |
| Licence choice is the owner's call and may differ from MIT | Flagged as an explicit decision; plan does not assume a licence. |
| `keep_default_na=False` changes parsing for existing fixtures | Re-run `test`/`coverage`; the deterministic-dtype fix is covered by new positive tests on the seed fixture. |
| Raising `fail_under` could fail CI if a branch dips | Set the floor at a defensible margin below the achieved 88% (≈85), and gate the omit-list via audit. |
| Scope creep into the Deferred Backlog | Non-Goals are explicit; Phase 3 is marked non-blocking. |
