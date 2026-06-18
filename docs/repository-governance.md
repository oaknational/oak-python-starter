# Repository Governance

This repository enforces most of its quality bar **in code** — the `check-ci`
gate sequence, the `repo_audit.py` self-checks (including `audit_supply_chain`,
which pins every workflow action to a SHA and keeps Dependabot watching both
ecosystems), and the SonarCloud pull-request gate. Those need no manual setup.

A few protections can only be set in **GitHub repository/organisation settings**
and cannot be expressed in the repo. This page is the canonical owner-action
checklist for them. An adopter of this template should work through it once for
their own repository.

## Already enforced by the `main` ruleset

The active "Protect default branch" ruleset already requires:

- a **pull request** to change `main` (no direct pushes);
- the **CodeQL `code_quality`** check to pass before merge;
- **no branch deletion** and **no force-push** (non-fast-forward) on `main`.

## Owner actions outstanding

These are settings changes a repository owner must make by hand. Each closes a
gap the in-repo gates structurally cannot.

1. **Make CI a real merge gate (highest priority).**
   Add **`Quality gates`** and **`Secret scanning (gitleaks)`** to the `main`
   ruleset's *required status checks*. Today the ruleset requires a PR and the
   CodeQL check, but **not** these two — so `main` can go red and a PR can still
   merge. This is the single biggest enforcement gap.

2. **Give the release PR a token.**
   The standing release PR is opened by `GITHUB_TOKEN`, so `ci.yml` does not run
   on it and it sits `UNSTABLE` indefinitely (merge it with
   `gh pr merge <n> --squash --auto`). Provide `create-pull-request` with a PAT
   or GitHub App token so `ci.yml` runs on the release PR; it then goes `CLEAN`
   and merges without `--auto`. See [Releases](dev-tooling.md#releases).

3. **Enable GitHub Code Quality (organisation preview).**
   Coverage is uploaded as Cobertura on every PR, but the upload runs with
   `fail-on-error: false`, so until the org enables the Code Quality preview it
   is a harmless no-op rather than a visible PR signal. See
   [Coverage reporting](dev-tooling.md#coverage-reporting).

4. **Protect release tags.**
   Add a tag ruleset for `v*` so release tags cannot be force-moved or deleted.
   There is currently no tag ruleset; only the branch ruleset above exists.

## Why these stay manual

Repository and organisation settings are owner-controlled and live outside the
tree, so the repo cannot assert them the way it asserts code and config. Keeping
the list here — rather than only in session notes — means a future owner or an
adopter can audit governance against reality without replaying project history.
