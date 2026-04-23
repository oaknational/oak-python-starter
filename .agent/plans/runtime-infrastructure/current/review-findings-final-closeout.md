---
name: "Final Review Findings Closeout"
overview: "Finish the runtime closeout on the smallest blocker-only path to commit: land the remaining must-fix reviewer findings, rerun the canonical validation once, rerun whole-repo reviewers once, then close."
todos:
  - id: blocker-fixes
    content: "Finish only the remaining blocker-level reviewer findings in hook parsing, repo-audit fail-closed behaviour, and active continuity truth surfaces."
    status: completed
  - id: blocker-proof
    content: "Add only the direct monkeypatch-free regression proof needed to lock those blocker fixes."
    status: completed
  - id: final-validation
    content: "Run uv run pytest, uv run python -m oaknational.python_repo_template.devtools check, and uv run python -m oaknational.python_repo_template.devtools check-ci once on the final diff."
    status: completed
  - id: final-review-and-close
    content: "Rerun the whole-repo reviewer set once, refresh continuity, and commit if no actionable findings remain."
    status: completed
---

# Final Review Findings Closeout

**Last Updated**: 2026-04-23  
**Status**: 🟢 COMPLETE  
**Scope**: Close the remaining whole-repo reviewer findings after the landed
runtime hardening tranche so the next session can finish the repo cleanly.

## End Goal

Leave the template in a state where its published command surface, hook
guardrails, support matrix, repo audit, and direct regression proof all make
truthful and measurable claims. The next session is intended to be the final
session for this branch-primary runtime tranche.

## Tight Commit Path

This plan is now deliberately narrower than the earlier hardening frame.

The effect we want is not "maximally hardened". The effect we want is
"truthfully ready to commit". That means:

- fix the remaining blocker-level reviewer findings
- prove those fixes directly without reopening adjacent surfaces
- run the canonical validation sequence once on the final diff
- rerun whole-repo review once
- close continuity and commit

Anything that is not needed for that path is out of scope for this tranche.

## Context

The earlier reviewer and implementation passes already landed the major runtime
contract changes:

- dependency hygiene, gate-contract centralisation, and repo-audit tightening
  are landed
- Windows drive-path handling, redirect blocking, strict pyright alignment, and
  no-monkeypatch enforcement are landed
- the published command-surface decision is made and documented:
  `activity-report` is the only published console script, while repo-local
  developer gates run through
  `uv run python -m oaknational.python_repo_template.devtools <gate>`
- Gemini hooks are treated as supported and aligned across the matrix, ADR, and
  native activation
- `uv run pytest` and
  `uv run python -m oaknational.python_repo_template.devtools check` now pass
  on the repaired diff after the latest reviewer-triggered follow-up edits

The latest whole-repo reviewer rerun then found a smaller set of genuine
blockers plus some optional tightenings. This plan now takes only the blocker
path.

## Already Decided

- **Published command surface**: `activity-report` remains the only published
  console script for the installed wheel. The repo cannot keep `uv run <gate>`
  as a truthful local command without also publishing those same entry points in
  wheel metadata, because `uv` resolves Python entry points from
  `[project.scripts]` and does not provide a separate repo-local Python command
  table. Repo-local developer gates therefore move to
  `uv run python -m oaknational.python_repo_template.devtools <gate>` and stay
  documented as source-checkout workflows only. `devtools.py` remains shipped as
  internal implementation detail, but it is explicitly out of the installed
  wheel contract; the published runtime proof stays limited to
  `activity-report` and `python -m oaknational.python_repo_template`.
- **Gate contract split**: the canonical gate contract must stop modelling
  repo-local developer gates as public scripts. The source of truth therefore
  splits into repo-local gate commands versus published wheel entry points
  rather than preserving the old `public_commands` shape under a new name.
- **Gemini hook support**: Gemini hooks are supported and must be treated as
  supported everywhere. The repo already ships native Gemini activation in
  `.gemini/settings.json`, `tools/agent_hooks.py` already implements Gemini
  `session-start` and `pre-tool` branches, and Gemini CLI's current
  configuration and hook docs expose `hooks.SessionStart` and
  `hooks.BeforeTool`.
- **Equivalent hook-bypass forms**: alongside `--no-verify`, treat
  token-aware `SKIP` environment assignments or exports that select
  `quality-gates` or `commitizen-commit-msg` as explicit hook-bypass attempts
  when paired with hook-triggering commands such as `git commit` and
  `git push`. Keep the broader generic skip flags named in
  `no-verify-requires-fresh-authorisation` blocked with the same command-context
  scoping, and prove both blocked and allowed forms directly.

## Current Closeout State

- Hook-runtime hardening is now landed for wrapped shell launchers,
  newline-carried exports, explicit hook-disabling config overrides, alias and
  dynamic git-config indirection, and force-push forms.
- `/usr/bin/env bash -lc ...` and `/usr/bin/env /bin/bash -lc ...` wrappers are
  now treated as equivalent env-launcher forms, so hook-bypass inspection no
  longer misses those shell-entry paths.
- The shipped gate contract is runtime-only again, while repo-audit now reads a
  separate repo-local command-surface contract for published entry points,
  legacy command denial, and documentation expectations.
- Direct proof now covers malformed top-level hook config shapes, the temporary
  build probe, the installed-wheel smoke workflow, UNC/authority-style
  activity-source rejection, env-path shell wrappers, and unknown documented
  repo-local commands.
- The final whole-repo reviewer rerun is now clean across code, architecture,
  test, security, and config review, and the canonical validation trilogy has
  been rerun successfully on the repaired 75-test candidate.

## Tight Execution Outline

### Step 1 — Finish only the blocker fixes

- complete the hook-runtime parsing fixes for wrapped `git` forms and explicit
  hook-disabling config overrides
- make `repo_audit` fail closed on non-object JSON and non-mapping hook YAML
- close the async and alias bypasses in the Python no-monkeypatch audit
- update only the live continuity and active-plan surfaces that still describe
  the pre-split command surface or pre-closeout state

### Step 2 — Add only the proof required by those fixes

- add direct `agent_hooks` regressions for the newly blocked shell forms
- add direct `repo_audit` regressions for malformed top-level config shapes
- add direct `repo_audit` regressions for the async and alias bypasses
- do not widen proof to adjacent already-green surfaces unless a failing test
  or reviewer finding requires it

### Step 3 — Validate once on the final diff

- run `uv run pytest`
- run `uv run python -m oaknational.python_repo_template.devtools check`
- run `uv run python -m oaknational.python_repo_template.devtools check-ci`

### Step 4 — Review once and close

- rerun the whole-repo reviewer set once on the final green state
- if no actionable findings remain, refresh continuity and close the tranche
- commit immediately after the closeout surfaces are truthful

## Explicit Deferrals

- do not reopen the command-surface decision; it is already made
- do not add broader audit abstractions, extra command-surface centralisation,
  or speculative proof for already-green paths unless a blocker forces it
- do not treat optional reviewer tightenings as part of this tranche after the
  next whole-repo rerun; if something non-blocking remains, record it and
  defer it

## Commit Evidence

This tranche is ready to commit only when all of the following are true:

- the blocker fixes above are landed
- the three canonical validation commands pass on the final diff
- the final whole-repo reviewer rerun reports no unresolved actionable issue
- active continuity surfaces describe this runtime tranche as complete

## Foundation Alignment

- **Principles**: preserve one source of truth, fail fast with specific
  messages, remove misleading surfaces instead of layering compatibility
- **Testing strategy**: use deterministic direct proof, avoid monkeypatching,
  and keep repo-state contracts in dedicated tooling where appropriate
- **Orientation**: canonical content stays in `.agent/`; platform directories
  remain thin projections; plans own live scope
- **Data boundary doctrine**: keep remote and local input validation explicit
  and centralised at the boundary
- **ADR-0001**: unsupported states must be explicit and enforced, and wrapper
  thinness is part of the contract
- **Rules**: `no-monkeypatching-in-python-tests` and
  `no-verify-requires-fresh-authorisation` stay load-bearing

## Quality Gates

- focused proof during implementation:
  - `uv run pytest tests/test_agent_hooks.py tests/test_devtools.py tests/test_repo_audit.py`
  - `uv run pytest tests/test_activity_store.py`
- final validation:
  - `uv run pytest`
  - `uv run python -m oaknational.python_repo_template.devtools check`
  - `uv run python -m oaknational.python_repo_template.devtools check-ci`

## Risk Assessment

| Risk | Mitigation |
| --- | --- |
| Changing the published command surface could break the established local developer ergonomics. | Make the command-surface decision explicit in Phase 0, then update hooks, docs, smoke proof, and audit in the same landing. |
| Hardening repo audit too aggressively could create brittle false positives. | Prefer structural parsing of small canonical files and add failing regression fixtures for each new rule. |
| Reconciling Gemini support incorrectly could create a false support claim or remove a live activation by accident. | Compare the matrix, ADR, and native config first, then choose one support stance and enforce it everywhere together. |
| Hook-policy tightening could miss equivalent bypasses or overmatch unrelated commands. | Record the exact bypass forms in Phase 0 and add direct `agent_hooks` tests for both blocked and allowed shell commands. |
