---
name: "Release Automation"
overview: "Automate versioned GitHub Releases with a committed version via the release-PR pattern (release-please), respecting the protected main ruleset."
todos:
  - id: red
    content: "RED: add failing audit_release_workflow tests (positive + negative cases)."
    status: pending
  - id: green
    content: "GREEN: add release-please config + release.yml + audit_release_workflow."
    status: pending
  - id: refactor
    content: "REFACTOR: document the release flow in README and docs/dev-tooling.md."
    status: pending
  - id: gates
    content: "Run the canonical quality gates (check / check-ci)."
    status: pending
  - id: review
    content: "Run config, security, test, and code reviewers; resolve findings."
    status: pending
---

# Release Automation

**Last Updated**: 2026-06-17  
**Status**: 🟡 PLANNING  
**Scope**: Automate versioned GitHub Releases with a committed version, via the release-PR pattern (release-please), under the protected `main` ruleset.

## End Goal

Merging a `feat`/`fix` change to `main` produces a versioned release with no
manual steps: an auto-maintained "release" PR bumps the **committed**
`pyproject.toml [project].version` and `CHANGELOG.md`, and merging that one-click
PR creates the Git tag `vX.Y.Z` and a GitHub Release with notes and the built
wheel + sdist attached. Today the repo has no release mechanism (zero tags, zero
releases, no changelog, a static version).

## Mechanism

`main` is governed by a repository ruleset (PRs required, direct branch pushes
blocked; confirmed live — ruleset `15388203`: `deletion, non_fast_forward,
pull_request, code_quality`, no required status checks, no tag protection). A
**committed** version therefore cannot be bumped by a workflow that pushes
straight to `main`. The canonical way to keep a committed version under branch
protection is the **release-PR pattern**: the version bump is itself a PR, so it
flows through the normal protected path; no bypass token, no weakening of the
ruleset. `release-please` is the maintained, purpose-built tool for this and
updates a PEP 621 `[project].version` via its TOML `extra-files` updater
(`jsonpath: "$.project.version"`). Creating a tag and GitHub Release on PR merge
is allowed because tags are outside the branch ruleset.

## Context

- Build backend is `hatchling`; `pyproject.toml` has a static
  `version = "0.1.0"`. Owner wants the version **committed in the repo**, not
  derived dynamically from tags.
- `commitizen` already enforces conventional commits at `commit-msg`
  (`version_provider = "uv"`, pinned by `audit_commit_workflow`). It stays for
  message enforcement; `release-please` consumes that history to drive releases.
- A plan-time architecture review confirmed: tag pushes/releases are unaffected
  by the branch ruleset; the committed-version pivot removes the build-backend
  and `version_provider` changes the earlier dynamic-versioning sketch would have
  required (so `audit_commit_workflow` and its tests are untouched); and the
  ruleset has no required status checks, so a `GITHUB_TOKEN`-opened release PR is
  still mergeable.
- Publish target: **GitHub Releases only** (wheel + sdist as assets); no PyPI.

## Existing Capabilities

- `.github/workflows/ci.yml` (quality gates + secret scan + coverage) — the
  release flow is a separate `release.yml`, leaving `ci.yml` untouched.
- The `check-ci` `build` gate already builds + smoke-tests a wheel via
  `hatchling` (`_run_build_probe` in
  `src/oaknational/python_repo_template/devtools.py`) — reused to produce the
  release artifacts; the committed version means the wheel is correctly
  versioned with no tag-fetch gymnastics.
- `audit_ci_workflow` in `tools/repo_audit.py` is the worked example for the new
  `audit_release_workflow` governance check.

## Non-Goals

- PyPI publishing / trusted publishing (GitHub Releases only).
- Dynamic / tag-derived versioning (the version stays committed).
- Bypass-token or direct-push-to-`main` releases (would weaken the ruleset).
- SHA-pinning the release-please action (the deferred supply-chain PR owns
  SHA-pinning across all workflows; this PR matches the existing `@vN` tag
  convention).

## Build-vs-Buy Attestation

- **What was searched**: `python-semantic-release`, a bespoke `cz bump` + PR
  workflow, and `release-please`.
- **What was found**: `python-semantic-release` pushes the bump to `main`
  (needs a ruleset bypass token); a bespoke `cz bump` + PR workflow is fragile
  glue; `release-please` (Google) is purpose-built for release-PR flows on
  branch-protected repos and updates a PEP 621 version via its TOML updater.
- **Why this shape was chosen**: `release-please` is the canonical, maintained
  fit, avoids bespoke glue and protection bypass, and composes with the existing
  Commitizen (message enforcement vs release orchestration — distinct roles).

## Reviewer Scheduling

- **Plan-time**: architecture reviewer — done (validated the ruleset/tag facts
  and the committed-version pivot).
- **Mid-cycle**: `config-reviewer` (workflow + release-please config +
  permissions + pinning); `security-reviewer` (`contents`/`pull-requests: write`
  scope, release-PR token model); `test-reviewer` (the new audit tests).
- **Close**: `code-reviewer` for whole-change coherence.

## WS1 — RED

- failing proof files:
  - `tests/test_repo_audit.py` — `audit_release_workflow` positive case +
    independent negative cases (missing/incorrect trigger; missing
    release-please step; config missing the `pyproject.toml`/`$.project.version`
    extra-files entry).
- acceptance criteria:
  - the new proofs fail for the expected reason before the auditor exists.

## WS2 — GREEN

- implementation files:
  - `release-please-config.json` — `release-type: "python"`,
    `include-component-in-tag: false`, `extra-files` TOML updater for
    `pyproject.toml` `$.project.version`.
  - `.release-please-manifest.json` — `{ ".": "0.1.0" }` to anchor the current
    version.
  - `.github/workflows/release.yml` — `on: push: [main]`; job `release-please`
    (`contents: write`, `pull-requests: write`) running the release-please
    action; job `publish-artifacts` gated on `releases_created` that builds with
    `uv build` and `gh release upload <tag> dist/*`.
  - `tools/repo_audit.py` — `audit_release_workflow`; register in
    `DEFAULT_AUDIT_CHECKS`; add the three new files to `REQUIRED_PATHS`.
- deterministic validation:
  - `uv run python -m oaknational.python_repo_template.devtools repo-audit`
  - `uv run python -m oaknational.python_repo_template.devtools check`

## WS3 — REFACTOR

- `README.md`: a "Releases" section (conventional commits → release PR → merge →
  tag + GitHub Release; the version lives in `pyproject.toml`).
- `docs/dev-tooling.md`: a "Releases" subsection; note Commitizen enforces the
  commit format release-please consumes (`version_provider` stays `uv`).
- keep the proofs green.

## Quality Gates

```bash
uv run python -m oaknational.python_repo_template.devtools check-ci
```

## Risk Assessment

| Risk | Mitigation |
| --- | --- |
| Release PR opened by `GITHUB_TOKEN` does not trigger CI on itself | Ruleset requires a PR but no status checks, so it is still mergeable; recommend an owner-provided PAT/GitHub App token so the release PR runs the gates for visibility. Documented, not blocking. |
| Release noise (too many releases) | Only `feat`/`fix`/breaking produce a version; the release PR batches changes, so releases are deliberate. |
| Unpinned action SHA | Deferred to the queued supply-chain PR (matches the existing `@vN` convention); logged, not silent. |
| First release bootstrap | `.release-please-manifest.json` seeded at `0.1.0`; the first qualifying merge proposes the next version with no manual tag. |

## Documentation Propagation

- `.agent/practice-core/practice.md`: no change — release automation is runtime
  infrastructure, not a Practice-method change.
- `.agent/practice-index.md`: no change.
- additional docs: `README.md` + `docs/dev-tooling.md` gain a Releases section;
  `tools/repo_audit_contract.toml` unchanged unless the auditor pins config
  values (decide during GREEN).

## Done When

1. Merging a `feat`/`fix` to `main` yields a release PR; merging it creates tag
   `vX.Y.Z` + a GitHub Release with notes and wheel + sdist attached, with the
   committed `pyproject.toml` version bumped.
2. `audit_release_workflow` + tests are green; full `check` is green; `main`
   stays green.
3. Reviewer findings are resolved or explicitly routed.
4. README + `docs/dev-tooling.md` document the flow.
