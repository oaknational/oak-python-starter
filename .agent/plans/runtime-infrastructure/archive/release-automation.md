---
name: "Release Automation"
overview: "Automate versioned GitHub Releases with a committed version via a Commitizen-driven release-PR, using a custom bump map (feat/fix=minor, else=patch, major manual-only), under the protected main ruleset."
todos:
  - id: red
    content: "RED: add failing audit_release_workflow + bump-policy audit tests (positive + negatives)."
    status: pending
  - id: green
    content: "GREEN: add Commitizen bump_map config + release.yml release-PR workflow + audit_release_workflow."
    status: pending
  - id: refactor
    content: "REFACTOR: document the release flow + versioning policy in README and docs/dev-tooling.md."
    status: pending
  - id: gates
    content: "Run the canonical quality gates (check / check-ci)."
    status: pending
  - id: review
    content: "Run config, security, test, and code reviewers; resolve findings."
    status: pending
---

# Release Automation

**Last Updated**: 2026-06-18  
**Status**: ✅ ARCHIVED 2026-06-18 — DELIVERED & LIVE-VERIFIED (PRs #20/#22 merged; `v0.1.0` + `v0.2.0` released). Durable doctrine homed in README "## Releases", `docs/dev-tooling.md`, the `release.yml` comment, `tools/release_increment.py`, and `audit_release_workflow`. The `--auto`/UNSTABLE merge mechanic lives in the gate-expansion thread record (still needed for the open release PR #25).  
**Scope**: Automate versioned GitHub Releases with a committed version and a custom bump policy, via a Commitizen-driven release-PR, under the protected `main` ruleset.

> **Delivered note (2026-06-18):** Live verification caught a real bug —
> `cz_conventional_commits` ignores `[tool.commitizen].bump_map`, so the custom
> policy is computed by `tools/release_increment.py` and applied via
> `cz bump --increment`. The standing release PR is opened by `GITHUB_TOKEN` so
> `ci.yml` does not run on it; it sits `UNSTABLE` and must be merged with
> `gh pr merge <n> --squash --auto` (not `--admin`). See the thread record.

## End Goal

Merging changes to `main` produces a versioned release with no manual steps for
minor/patch: an auto-maintained "release" PR bumps the **committed**
`pyproject.toml [project].version` and `CHANGELOG.md` per the owner's bump
policy, and merging that one-click PR creates the Git tag `vX.Y.Z` and a GitHub
Release with notes and the built wheel + sdist attached. Major versions are cut
deliberately by hand. Today the repo has no release mechanism (zero tags, zero
releases, no changelog, a static version).

## Versioning policy (owner-defined)

Bump level is computed from the Conventional Commit types since the last tag,
highest wins:

| Commit type(s) | Bump |
| --- | --- |
| `feat`, `fix` | minor |
| everything else (`chore`, `docs`, `perf`, `refactor`, `build`, `ci`, `test`, `style`, `revert`, …) | patch |
| `!` / `BREAKING CHANGE:` | **no auto-release** — a major is required and is cut manually |
| major | manual only, via `workflow_dispatch` (increment = major) |

Notes and deliberate deviations:

- `fix → minor` is intentional and **inverts the SemVer norm** (fix is normally
  patch). Accepted by the owner.
- "Everything else → patch" means even docs/chore changes cut a release; the
  release-PR batches merges, so this is one release per release-PR-merge, not one
  per commit.
- **Breaking-change safety**: the automation must never silently ship a breaking
  change inside a minor/patch. When a `!`/`BREAKING CHANGE` marker is present in
  the pending range, the auto-release stands down and signals that a deliberate
  major is due. (Lighter alternative the owner may later choose: let it ride as
  minor with a ⚠ BREAKING changelog flag — not the default.)
- The repo is at `0.1.0` (pre-1.0). The first manual major is effectively the
  `1.0.0` decision.

## Mechanism

`main` is governed by a repository ruleset (PRs required, direct branch pushes
blocked; confirmed live — ruleset `15388203`: `deletion, non_fast_forward,
pull_request, code_quality`, no required status checks, no tag protection). A
**committed** version therefore cannot be bumped by a workflow that pushes
straight to `main`. The canonical way to keep a committed version under branch
protection is the **release-PR pattern**: the version bump is itself a PR, so it
flows through the normal protected path — no bypass token, no weakening of the
ruleset. Creating a tag + GitHub Release on PR merge is allowed because tags are
outside the branch ruleset.

The custom bump policy above **cannot be expressed in `release-please`** (its
versioning strategies are fixed: breaking→major, feat→minor, fix→patch; per-type
remapping needs a bespoke TypeScript strategy class). **Commitizen** — already in
this repo — has a configurable `bump_map`/`bump_pattern`, so it can express
feat/fix→minor, else→patch, and the no-auto-major rule. We therefore drive the
release-PR with Commitizen rather than release-please.

## Context

- Build backend is `hatchling`; `pyproject.toml` keeps a static, **committed**
  `version` (owner wants the version in the repo, not derived from tags).
- `commitizen` already enforces conventional commits at `commit-msg` and is
  configured `version_provider = "uv"` (pinned by `audit_commit_workflow`). It
  now also performs the bump (writing the committed `pyproject` version), so
  `version_provider = "uv"` becomes actively used and the audit is **unchanged**.
- A plan-time architecture review confirmed: tag pushes/releases are unaffected
  by the branch ruleset; the committed-version approach needs no build-backend
  change; and the ruleset has no required status checks, so a
  `GITHUB_TOKEN`-opened release PR is still mergeable.
- Publish target: **GitHub Releases only** (wheel + sdist as assets); no PyPI.

## Existing Capabilities

- `commitizen` (dev dependency, `[tool.commitizen]`, `version_provider = "uv"`,
  commit-msg hook) — reused for both message enforcement and the bump.
- `.github/workflows/ci.yml` (quality gates + secret scan + coverage) —
  untouched; the release flow is a separate `release.yml`.
- The `check-ci` `build` gate already builds + smoke-tests a `hatchling` wheel
  (`_run_build_probe` in `src/oaknational/python_repo_template/devtools.py`) —
  reused to produce the release artifacts.
- `audit_ci_workflow` in `tools/repo_audit.py` is the worked example for the new
  `audit_release_workflow` governance check.

## Non-Goals

- PyPI publishing / trusted publishing (GitHub Releases only).
- Dynamic / tag-derived versioning (the version stays committed).
- Bypass-token or direct-push-to-`main` releases (would weaken the ruleset).
- Auto-major on breaking changes (major is deliberate, manual-only).
- SHA-pinning workflow actions (the deferred supply-chain PR owns that; this PR
  matches the existing `@vN` tag convention).

## Build-vs-Buy Attestation

- **What was searched**: `release-please`, `python-semantic-release` (PSR), and a
  Commitizen-driven release-PR.
- **What was found**: `release-please` is the cleanest off-the-shelf release-PR
  tool but its bump rules are fixed and **cannot express the custom policy**
  without a bespoke strategy class. `PSR` has a configurable commit parser but
  pushes the bump to `main` (needs a ruleset bypass token). `Commitizen` is
  already in the repo and its `bump_map`/`bump_pattern` express the policy
  exactly.
- **Why this shape was chosen**: BUILD a thin Commitizen-driven release-PR
  workflow — the off-the-shelf BUY options cannot meet the custom bump policy
  under protected `main`, and Commitizen avoids adding a second conventional-commit
  engine. The new code is glue (compute bump → bump branch → release PR → tag +
  release on merge), not a new abstraction.

## Reviewer Scheduling

- **Plan-time**: architecture reviewer — done (validated the ruleset/tag facts,
  the committed-version approach, and the tool re-evaluation).
- **Mid-cycle**: `config-reviewer` (workflow + Commitizen bump config +
  permissions + pinning); `security-reviewer` (`contents`/`pull-requests: write`
  scope, release-PR token model); `test-reviewer` (the new audit tests).
- **Close**: `code-reviewer` for whole-change coherence.

## WS1 — RED

- failing proof files:
  - `tests/test_repo_audit.py` — `audit_release_workflow` positive case +
    independent negatives (missing/incorrect `push: main` trigger; missing
    Commitizen bump step; `[tool.commitizen]` missing the custom `bump_map`
    entries that map `feat`/`fix`→MINOR and omit auto-MAJOR).
- acceptance criteria:
  - each proof fails for the expected reason before the auditor/config exists.

## WS2 — GREEN

- implementation files:
  - `pyproject.toml` `[tool.commitizen]` — add custom `bump_map`/`bump_pattern`
    (feat/fix→MINOR, catch-all→PATCH, no auto-MAJOR) and changelog options;
    **keep `version_provider = "uv"`**.
  - `.github/workflows/release.yml` — `on: push:[main]` + `workflow_dispatch`
    (input `increment` for manual major). Release-PR job (`contents: write`,
    `pull-requests: write`): detect breaking markers → stand down + signal manual
    major; else `cz bump --yes` on a release branch (writes committed version +
    `CHANGELOG.md`), open/refresh the release PR. Release job on the merged bump
    commit: create tag `vX.Y.Z`, `uv build`, `gh release upload <tag> dist/*`.
  - `tools/repo_audit.py` — `audit_release_workflow` (assert workflow triggers +
    Commitizen bump policy present); register in `DEFAULT_AUDIT_CHECKS`; add
    `release.yml` to `REQUIRED_PATHS`.
- deterministic validation:
  - `uv run python -m oaknational.python_repo_template.devtools repo-audit`
  - `uv run python -m oaknational.python_repo_template.devtools check`

## WS3 — REFACTOR

- `README.md`: a "Releases" section (commit → release PR → merge → tag + GitHub
  Release; the version lives in `pyproject.toml`; the bump table; major is
  manual).
- `docs/dev-tooling.md`: a "Releases" subsection documenting the bump policy and
  the manual-major `workflow_dispatch`.
- keep the proofs green.

## Quality Gates

```bash
uv run python -m oaknational.python_repo_template.devtools check-ci
```

## Risk Assessment

| Risk | Mitigation |
| --- | --- |
| Release PR opened by `GITHUB_TOKEN` does not trigger CI on itself | Ruleset requires a PR but no status checks, so it is still mergeable; recommend an owner-provided PAT/GitHub App token so the release PR runs the gates for visibility. Documented, not blocking. |
| `fix → minor` surprises consumers expecting SemVer | Documented prominently in README + changelog; owner-chosen. |
| Breaking change handling adds workflow complexity | Default to the safe stand-down + manual-major; keep the detection step small and tested; document the lighter ⚠-flag alternative. |
| Release noise from "everything → patch" | The release PR batches merges, so it is one release per release-PR-merge. |
| Unpinned action SHA | Deferred to the queued supply-chain PR (matches `@vN`); logged, not silent. |
| First release bootstrap | Seed an initial `v0.1.0` tag (or let the first `cz bump` start from the committed `0.1.0`). |

## Documentation Propagation

- `.agent/practice-core/practice.md`: no change — release automation is runtime
  infrastructure, not a Practice-method change.
- `.agent/practice-index.md`: no change.
- additional docs: `README.md` + `docs/dev-tooling.md` gain a Releases section;
  `tools/repo_audit_contract.toml` may pin the bump-policy values if the auditor
  enforces them (decide during GREEN).

## Done When

1. Merging a non-breaking change to `main` yields a release PR bumping the
   committed `pyproject` version + `CHANGELOG.md` per the policy; merging it
   creates tag `vX.Y.Z` + a GitHub Release with notes and wheel + sdist attached.
2. A breaking marker does not auto-release; a manual major can be cut via
   `workflow_dispatch`.
3. `audit_release_workflow` + tests are green; full `check` is green; `main`
   stays green.
4. Reviewer findings are resolved or explicitly routed.
5. README + `docs/dev-tooling.md` document the flow and the bump policy.
